"""kv_replay on a tiny REAL FastWAM MoT (Wan video DiT + ActionDiT, random weights, CPU): the replica of the action
layer, the zero start, the history prefill and its temporal re-rotation."""
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("einops")

from torch import nn  # noqa: E402

from fastwam.memory_v2.config import MemoryV2Config  # noqa: E402
from fastwam.memory_v2.model import FastWAMActionAdapter, MemoryV2Model  # noqa: E402
from fastwam.memory_v2.replay import mot_replay_parts, recency_positions, rerotate_temporal  # noqa: E402

LAYERS, HEADS, HEAD_DIM, VIDEO, ACTION, TEXT = 3, 24, 24, 576, 64, 32   # 24 heads: FrozenBackbone hardcodes them


def _frozen():
    from fastwam.memory_s1.model import FrozenBackbone
    from fastwam.models.wan22.action_dit import ActionDiT
    from fastwam.models.wan22.mot import MoT
    from fastwam.models.wan22.wan_video_dit import WanVideoDiT
    torch.manual_seed(0)
    video = WanVideoDiT(hidden_dim=VIDEO, in_dim=48, ffn_dim=128, out_dim=48, text_dim=TEXT, freq_dim=32, eps=1e-6,
                        patch_size=(1, 2, 2), num_heads=HEADS, attn_head_dim=HEAD_DIM, num_layers=LAYERS,
                        has_image_input=False, seperated_timestep=True, fuse_vae_embedding_in_latents=True,
                        action_dim=14)
    action = ActionDiT(hidden_dim=ACTION, action_dim=14, ffn_dim=128, text_dim=TEXT, freq_dim=32, eps=1e-6,
                       num_heads=HEADS, attn_head_dim=HEAD_DIM, num_layers=LAYERS)
    frozen = FrozenBackbone.__new__(FrozenBackbone)
    nn.Module.__init__(frozen)
    frozen.mot = MoT({"video": video, "action": action}, mot_checkpoint_mixed_attn=False)
    frozen.proprio_encoder = nn.Linear(14, TEXT)
    # random weights: lift the zero-initialised output layers so the layers actually do something
    with torch.no_grad():
        for p in frozen.parameters():
            if p.abs().sum() == 0:
                p.normal_(0, 0.02)
    return frozen.to(torch.bfloat16).eval().requires_grad_(False)


def _batch(k=3, b=2, seed=0):
    g = torch.Generator().manual_seed(seed)
    frame_ids = torch.tensor([[0, 8, 16], [0, 24, 0]])[:, :k]
    valid = torch.tensor([[True, True, True], [True, True, False]])[:, :k]
    return {"latent": torch.randn(b, 48, 1, 24, 20, generator=g), "text": torch.randn(b, 5, TEXT, generator=g),
            "proprio": torch.randn(b, 14, generator=g), "actions": torch.randn(b, 32, 14, generator=g),
            "hist_latent": torch.randn(b, k, 48, 1, 24, 20, generator=g), "hist_proprio": torch.randn(b, k, 14, generator=g),
            "frame_ids": frame_ids, "roles": torch.tensor([[0, 1, 2], [0, 2, 0]])[:, :k], "history_valid": valid,
            "current_ids": torch.tensor([24, 32])}


def _cfg():
    return MemoryV2Config(video_dim=VIDEO, action_hidden=ACTION, memory_dim=32, heads=4, injection_layers=(1,),
                          num_action_layers=LAYERS, read="kv_replay", replay_rank=4, replay_chunk=2, tau_gate_hidden=8)


def test_replica_is_the_released_layer_and_zero_start_is_exact():
    frozen = _frozen()
    adapter = FastWAMActionAdapter(frozen)
    model = MemoryV2Model(adapter, _cfg())
    batch = _batch()
    x = torch.randn(2, 32, 14)
    t = torch.full((2,), 700.0)
    with torch.no_grad():
        c = model.conditions(batch)
        h, aux = adapter.prepare(x, t, c.context)
        keys, values = c.current_kv
        for index in range(LAYERS):
            ref = adapter.block(index, h, aux, c.current_kv)
            k, v = model.memory.replay.layer_kv(c.replay, model.memory.replay.slot(index))
            with_h, without = mot_replay_parts(frozen.mot, index, h, aux, keys[index], values[index], k, v,
                                               c.replay.token_valid)
            assert torch.equal(without, ref)                 # same calls, same order: bit-identical
            assert not torch.equal(with_h, ref)
            h = ref
        off = model.velocity(x, t, c, "off")
        assert torch.equal(model.velocity(x, t, c, "on"), off) and torch.equal(model.velocity(x, t, c, "null"), off)
    c = model.conditions(batch)
    model.velocity(x, t, c, "on").float().square().mean().backward()     # through the checkpointed delta
    assert float(model.memory.replay.gate.net[2].weight.grad.abs().sum()) > 0


def test_history_kv_is_the_frame_prefilled_alone_then_moved_back_in_time():
    frozen = _frozen()
    adapter = FastWAMActionAdapter(frozen)
    model = MemoryV2Model(adapter, _cfg())
    batch = _batch()
    state = model.conditions(batch).replay
    positions = recency_positions(batch["frame_ids"], batch["history_valid"])
    assert positions.tolist() == [[-3, -2, -1], [-2, -1, 0]]
    _, kv, _ = frozen.encode_observation(batch["hist_latent"][1, 1:2], batch["text"][1:2], batch["hist_proprio"][1, 1:2])
    for layer in range(LAYERS):
        expected = rerotate_temporal(kv[0][layer][:, None], torch.tensor([[-1]]), HEADS)[:, 0]
        got = state.keys[layer].reshape(2, 3, 120, -1)[1, 1]
        assert torch.equal(got, expected[0])
        assert torch.equal(state.values[layer].reshape(2, 3, 120, -1)[1, 1], kv[1][layer][0])
        assert float(state.keys[layer].reshape(2, 3, 120, -1)[1, 2].abs().sum()) == 0      # padding slot
    assert state.token_valid.shape == (2, 360) and state.token_valid[1, 240:].sum() == 0


def test_replica_runs_with_fp32_action_weights_like_the_dense_abmodel():
    """11-06: the dense ABModel keeps fp32 ActionDiT weights and feeds bf16 tokens; the replica then runs under bf16
    autocast and stays close to the bf16-weight layer (same rounded weights)."""
    import copy
    frozen = _frozen()
    wide = copy.deepcopy(frozen)
    wide.mot.mixtures["action"].float()
    adapter = FastWAMActionAdapter(frozen)
    model = MemoryV2Model(adapter, _cfg())
    batch = _batch()
    x, t = torch.randn(2, 32, 14), torch.full((2,), 700.0)
    with torch.no_grad():
        c = model.conditions(batch)
        h, aux = adapter.prepare(x, t, c.context)
        keys, values = c.current_kv
        k, v = model.memory.replay.layer_kv(c.replay, model.memory.replay.slot(1))
        a_with, a_without = mot_replay_parts(frozen.mot, 1, h, aux, keys[1], values[1], k, v, c.replay.token_valid)
        b_with, b_without = mot_replay_parts(wide.mot, 1, h, aux, keys[1], values[1], k, v, c.replay.token_valid)
    for a, b in ((a_with, b_with), (a_without, b_without)):
        rel = float((a.float() - b.float()).norm() / a.float().norm())
        assert rel < 2e-2, rel
    h2 = h.detach().clone().requires_grad_(True)                     # and it differentiates (training path)
    w, wo = mot_replay_parts(wide.mot, 1, h2, aux, keys[1], values[1], k, v, c.replay.token_valid)
    (w - wo).float().square().mean().backward()
    assert h2.grad is not None and float(h2.grad.abs().sum()) > 0
