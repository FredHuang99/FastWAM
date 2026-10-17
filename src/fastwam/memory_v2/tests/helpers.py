"""Tiny CPU backbone implementing the memory_v2 adapter protocol (shared test helpers)."""
import torch
from torch import nn

from fastwam.memory_v2.config import HistoryPolicyConfig, MemoryV2Config
from fastwam.memory_v2.history import collate_history, select_history


class TinyBackbone(nn.Module):
    """Action tokens attend to per-layer 'current frame' KV derived from the latent, like the MoT."""

    def __init__(self, action_dim=5, hidden=24, layers=6, current_tokens=6, video_width=16):
        super().__init__()
        torch.manual_seed(0)
        self.num_action_layers = layers
        self.encoder = nn.Linear(video_width, hidden)
        self.kv = nn.ModuleList([nn.Linear(hidden, 2 * hidden) for _ in range(layers)])
        self.action_in = nn.Linear(action_dim, hidden)
        self.time = nn.Linear(1, hidden)
        self.q = nn.ModuleList([nn.Linear(hidden, hidden) for _ in range(layers)])
        self.mlp = nn.ModuleList([nn.Linear(hidden, hidden) for _ in range(layers)])
        self.head = nn.Linear(hidden, action_dim)
        self.requires_grad_(False)

    def encode(self, batch):
        current = self.encoder(batch["latent"])                  # [B, Tc, hidden]
        keys, values = [], []
        for layer in self.kv:
            k, v = layer(current).chunk(2, -1)
            keys.append(k)
            values.append(v)
        return (keys, values), batch["context"]

    def prepare(self, actions, timestep, context):
        x = self.action_in(actions) + self.time(timestep.float()[:, None, None] / 1000.0) + context[:, None, :]
        return x, None

    def block(self, index, x, aux, current_kv):
        keys, values = current_kv
        q = self.q[index](x)
        probs = (q @ keys[index].transpose(1, 2) / q.shape[-1] ** 0.5).softmax(-1)
        x = x + probs @ values[index]
        return x + torch.tanh(self.mlp[index](x))

    def post(self, x, aux):
        return self.head(x)


TINY = dict(video_dim=16, action_hidden=24, memory_dim=32, heads=4, grid=(4, 3), pool=(1, 1),
            injection_layers=(1, 3, 5), num_action_layers=6, null_tokens=2, time_features=16,
            spatial_features=8, tau_gate_hidden=8)


def make_batch(batch=3, horizon=8, action_dim=5, episode_length=40, seed=0, cfg=None, policy=None):
    cfg = cfg or MemoryV2Config(**TINY)
    policy = policy or HistoryPolicyConfig(anchor_frames=1, landmark_stride=8, recent_frames=1, recent_stride=4, max_frames=6)
    generator = torch.Generator().manual_seed(seed)
    tokens = cfg.grid[0] * cfg.grid[1]
    episodes = torch.randn(batch, episode_length, tokens, cfg.video_dim, generator=generator)
    currents = [10 + 9 * b for b in range(batch)]
    selections, features = [], []
    for b, current in enumerate(currents):
        selection = select_history(range(current + 1), current, policy)
        selections.append(selection)
        features.append([episodes[b, i] for i in selection.ids])
    history = collate_history(features, selections, tokens, cfg.video_dim, dtype=torch.float32)
    out = {"latent": torch.randn(batch, 6, 16, generator=generator),
           "context": torch.randn(batch, 24, generator=generator),
           "actions": torch.randn(batch, horizon, action_dim, generator=generator),
           "action_valid": torch.ones(batch, horizon, dtype=torch.bool)}
    out.update(history)
    out["_episodes"] = episodes
    return out
