"""11-27 (plan v21 6.6, RoboMME): FullModel.from_release takes the action / proprio sizes from the base payload."""
import torch

from fastwam.fullft.model import release_dims


def test_robotwin_layout_is_14_14():
    payload = {"mot": {"mixtures.action.action_encoder.weight": torch.zeros(1024, 14)},
               "proprio_encoder": {"weight": torch.zeros(3072, 14), "bias": torch.zeros(3072)}}
    assert release_dims(payload) == (14, 14)


def test_libero_layout_is_7_8():
    payload = {"mot": {"mixtures.action.action_encoder.weight": torch.zeros(1024, 7)},
               "proprio_encoder": {"weight": torch.zeros(3072, 8), "bias": torch.zeros(3072)}}
    assert release_dims(payload) == (7, 8)


def test_missing_keys_default_to_14():
    assert release_dims({}) == (14, 14)
