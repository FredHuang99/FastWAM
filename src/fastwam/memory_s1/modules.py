"""Trainable Reader and post-block history residuals; True means attend."""
from __future__ import annotations

import math

import torch
from torch import nn
from torch.nn import functional as F

INJECTION_LAYERS = (4, 9, 14, 19, 24, 29)


def position_encoding(ids, width):
    rate = torch.exp(-math.log(10000) * torch.arange(width // 2, device=ids.device).float() / (width // 2))
    phase = ids.float().unsqueeze(-1) * rate
    return torch.cat((phase.cos(), phase.sin()), -1)


class Attention(nn.Module):
    def __init__(self, width=1024, heads=8):
        super().__init__()
        self.heads = heads
        self.q = nn.Linear(width, width)
        self.k = nn.Linear(width, width)
        self.v = nn.Linear(width, width)
        self.out = nn.Linear(width, width)

    def forward(self, query, source, valid=None):
        def split(x):
            return x.unflatten(-1, (self.heads, x.shape[-1] // self.heads)).transpose(1, 2)
        mask = None if valid is None else valid[:, None, None, :]
        x = F.scaled_dot_product_attention(split(self.q(query)), split(self.k(source)),
                                          split(self.v(source)), attn_mask=mask, dropout_p=0.0)
        return self.out(x.transpose(1, 2).flatten(2))


class ReaderBlock(nn.Module):
    def __init__(self):
        super().__init__()
        self.cross_q_norm = nn.LayerNorm(1024, eps=1e-6)
        self.cross_kv_norm = nn.LayerNorm(1024, eps=1e-6)
        self.cross = Attention()
        self.self_norm = nn.LayerNorm(1024, eps=1e-6)
        self.self_attention = Attention()
        self.ffn_norm = nn.LayerNorm(1024, eps=1e-6)
        self.ffn = nn.Sequential(nn.Linear(1024, 4096), nn.GELU(), nn.Linear(4096, 1024))

    def forward(self, query, history, valid):
        query = query + self.cross(self.cross_q_norm(query), self.cross_kv_norm(history), valid)
        normed = self.self_norm(query)
        query = query + self.self_attention(normed, normed)
        return query + self.ffn(self.ffn_norm(query))


class Injector(nn.Module):
    def __init__(self):
        super().__init__()
        self.q_norm = nn.LayerNorm(1024, eps=1e-6)
        self.kv_norm = nn.LayerNorm(1024, eps=1e-6)
        self.attention = Attention()
        self.gate = nn.Parameter(torch.tensor(1e-3, dtype=torch.float32))

    def forward(self, action, readout, gate_scale=1.0):
        # Only the explicit diagnostic override bypasses the memory path.
        if gate_scale == 0:
            return action
        return action + (self.gate * gate_scale).to(action.dtype) * self.attention(self.q_norm(action), self.kv_norm(readout))


class MemoryModules(nn.Module):
    def __init__(self):
        super().__init__()
        self.queries = nn.Parameter(torch.empty(32, 1024))
        self.history_projection = nn.Linear(3072, 1024)
        self.text_projection = nn.Linear(4096, 1024)
        self.proprio_projection = nn.Linear(14, 1024)
        self.reader = nn.ModuleList([ReaderBlock() for _ in range(4)])
        self.injectors = nn.ModuleDict({str(i): Injector() for i in INJECTION_LAYERS})
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)
        nn.init.normal_(self.queries, std=0.02)

    def read(self, current, text, text_valid, proprio, history, frame_ids, history_valid):
        if history.shape[2:] != (120, 3072) or (history_valid.sum(1) == 0).any():
            raise ValueError("History must contain at least the current frame and have 120x3072 features.")
        if (text_valid.sum(1) == 0).any():
            raise ValueError("Task instruction cannot be empty.")
        text_mean = (text * text_valid[..., None]).sum(1) / text_valid.sum(1, keepdim=True)
        query = (self.queries[None] + self.history_projection(current.mean(1))[:, None]
                 + self.text_projection(text_mean)[:, None] + self.proprio_projection(proprio)[:, None])
        history_tokens = self.history_projection(history)
        temporal = position_encoding(frame_ids, 1024)[:, :, None, :]
        rows = torch.arange(12, device=history.device).repeat_interleave(10)
        cols = torch.arange(10, device=history.device).repeat(12)
        spatial = torch.cat((position_encoding(rows, 512), position_encoding(cols, 512)), -1)
        source = (history_tokens + temporal + spatial[None, None]).flatten(1, 2)
        valid = history_valid.repeat_interleave(120, dim=1)
        for block in self.reader:
            query = block(query, source, valid)
        return query

    def parameter_groups(self):
        decay, no_decay = [], []
        for name, parameter in self.named_parameters():
            exclude = parameter.ndim < 2 or "norm" in name or name == "queries"
            (no_decay if exclude else decay).append(parameter)
        return [{"params": decay, "weight_decay": 0.01}, {"params": no_decay, "weight_decay": 0.0}]
