# SYNTHETIC  - An AI-Orchestrated Engine for Multi-Modal Traffic Scenario Synthesis
# Copyright (C) 2026 Noxfort Systems 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SOFTWARE.
#
# File: src/models/st_gatv2.py
# Author: Gabriel Moraes
# Date: 2026-10-06

import math
from typing import Any, Optional, Union
import torch
import torch.nn as nn
import torch.nn.functional as F

class Time2Vec(nn.Module):
    """
    Learnable periodic temporal representation for continuous time-of-day.
    Decomposes seconds into linear trend and harmonic sinusoidal components.
    t2v(tau)[0] = w0 * tau + b0
    t2v(tau)[1:] = sin(wi * tau + bi)
    """

    def __init__(self, out_dim: int = 16):
        super().__init__()
        self.out_dim = out_dim
        self.w0 = nn.Parameter(torch.randn(1))
        self.b0 = nn.Parameter(torch.zeros(1))
        self.w = nn.Parameter(torch.randn(out_dim - 1))
        self.b = nn.Parameter(torch.zeros(out_dim - 1))

    def forward(self, tau: torch.Tensor) -> torch.Tensor:
        """
        tau: [N, 1] continuous seconds in day [0.0, 86400.0]
        Returns: [N, out_dim]
        """
        if tau.dim() == 0:
            tau = tau.unsqueeze(0).unsqueeze(0)
        elif tau.dim() == 1:
            tau = tau.unsqueeze(-1)

        # Normalize 24-hour cycle to [0, 2pi]
        tau_norm = (tau % 86400.0) * (2.0 * math.pi / 86400.0)

        linear = self.w0 * tau_norm + self.b0
        periodic = torch.sin(tau_norm * self.w + self.b)
        return torch.cat([linear, periodic], dim=-1)

def get_tidal_bias(time_sec: float, day_of_week: int = 0) -> float:
    """
    Computes directional tidal bias conditioned on time of day and day of week:
    +1.0 (towards city center) during weekday morning peak (08:00)
    -1.0 (towards suburbs/periphery) during weekday evening peak (18:00)
    Weekends feature decentralized, leisure-oriented routing without corporate commuter rush.
    """
    hour = (time_sec / 3600.0) % 24.0

    if day_of_week in (0, 1, 2, 3):  # Mon-Thu
        morning = 0.85 * math.exp(-((hour - 8.0) ** 2) / (2 * 1.5 ** 2))
        evening = -0.90 * math.exp(-((hour - 18.0) ** 2) / (2 * 1.8 ** 2))
        return float(max(-1.0, min(1.0, morning + evening)))

    elif day_of_week == 4:  # Friday
        morning = 0.80 * math.exp(-((hour - 8.0) ** 2) / (2 * 1.5 ** 2))
        # Enhanced weekend getaway outflow on Friday evening
        evening = -0.95 * math.exp(-((hour - 17.5) ** 2) / (2 * 2.2 ** 2))
        return float(max(-1.0, min(1.0, morning + evening)))

    elif day_of_week == 5:  # Saturday
        # No CBD commuter rush; decentralized leisure & commercial movement
        suburban_malls = -0.15 * math.exp(-((hour - 15.0) ** 2) / (2 * 2.5 ** 2))
        return float(max(-1.0, min(1.0, suburban_malls)))

    else:  # Sunday (day_of_week == 6)
        # Sunday evening return rush inwards to residential core
        evening_return = 0.35 * math.exp(-((hour - 19.0) ** 2) / (2 * 1.6 ** 2))
        return float(max(-1.0, min(1.0, evening_return)))

class STGATv2(nn.Module):
    """
    Spatio-Temporal Graph Attention Network v2 (ST-GATv2).
    Processes historical temporal sliding windows [N, T, F] alongside continuous
    diurnal time-of-day embeddings, and performs spatial multi-head attention
    to compute dynamic, tidal turning ratios alpha_ij.
    """

    def __init__(
        self,
        in_features: int = 4,
        time_dim: int = 16,
        hidden_dim: int = 32,
        num_heads: int = 2,
        temporal_window: int = 12
    ):
        super().__init__()
        self.in_features = in_features
        self.time_dim = time_dim
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.temporal_window = temporal_window

        # 1. Continuous Time-of-Day Encoder
        self.time2vec = Time2Vec(out_dim=time_dim)

        # 2. Gated Temporal Convolutional Layer (1D TCN) along time axis
        self.conv_filter = nn.Conv1d(
            in_channels=in_features,
            out_channels=hidden_dim,
            kernel_size=3,
            padding=1
        )
        self.conv_gate = nn.Conv1d(
            in_channels=in_features,
            out_channels=hidden_dim,
            kernel_size=3,
            padding=1
        )
        self.temp_pool = nn.AdaptiveAvgPool1d(1)

        # Difference projection to capture acceleration / density build-up
        self.delta_proj = nn.Linear(in_features, hidden_dim)

        # 3. Spatial GATv2 Core
        spatial_in_dim = hidden_dim * 2 + time_dim
        self.lin_src = nn.Linear(spatial_in_dim, hidden_dim * num_heads, bias=False)
        self.lin_dst = nn.Linear(spatial_in_dim, hidden_dim * num_heads, bias=False)
        self.att = nn.Parameter(torch.Tensor(1, num_heads, hidden_dim))
        self.out_proj = nn.Linear(num_heads, 1)

        self._reset_parameters()

    def _reset_parameters(self):
        nn.init.xavier_uniform_(self.lin_src.weight)
        nn.init.xavier_uniform_(self.lin_dst.weight)
        nn.init.xavier_uniform_(self.att)
        nn.init.xavier_uniform_(self.conv_filter.weight)
        nn.init.xavier_uniform_(self.conv_gate.weight)
        nn.init.zeros_(self.conv_filter.bias)
        nn.init.zeros_(self.conv_gate.bias)
        nn.init.xavier_uniform_(self.delta_proj.weight)
        nn.init.zeros_(self.delta_proj.bias)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        current_time_sec: Optional[Union[float, int, torch.Tensor]] = None,
        centripetal_scores: Optional[Union[torch.Tensor, Any]] = None,
        day_of_week: int = 0
    ) -> torch.Tensor:
        """
        x: [N, in_features] or [N, T, in_features] node state window
        edge_index: [2, E] source and destination indices
        current_time_sec: optional continuous simulation seconds for Time2Vec conditioning
        centripetal_scores: optional [N] array of directional alignment to city center in [-1.0, 1.0]
        day_of_week: 0=Monday ... 6=Sunday for tidal pattern selection
        Returns: [E] dynamic turning probabilities alpha_ij grouped and normalized by source node
        """
        num_edges = edge_index.size(1)
        if num_edges == 0:
            return torch.empty(0, device=x.device, dtype=x.dtype)

        # Handle both [N, F] and [N, T, F] formats
        if x.dim() == 2:
            num_nodes, in_feat = x.shape
            x_seq = x.unsqueeze(1).repeat(1, self.temporal_window, 1) # [N, T, F]
            delta = torch.zeros_like(x)
        elif x.dim() == 3:
            num_nodes, seq_len, in_feat = x.shape
            x_seq = x
            if seq_len > 1:
                delta = x[:, -1, :] - x[:, 0, :]
            else:
                delta = torch.zeros((num_nodes, in_feat), device=x.device, dtype=x.dtype)
        else:
            raise ValueError(f"Expected x of shape [N, F] or [N, T, F], got {x.shape}")

        # 1. Temporal Gated Convolution: [N, F, T]
        x_trans = x_seq.transpose(1, 2)
        h_filter = torch.tanh(self.conv_filter(x_trans))
        h_gate = torch.sigmoid(self.conv_gate(x_trans))
        h_gated = h_filter * h_gate # [N, hidden_dim, T]
        h_temp = self.temp_pool(h_gated).squeeze(-1) # [N, hidden_dim]

        # Trend / acceleration representation
        h_delta = self.delta_proj(delta) # [N, hidden_dim]

        # 2. Continuous Diurnal Embedding via Time2Vec
        if current_time_sec is not None:
            if isinstance(current_time_sec, (int, float)):
                t_tensor = torch.full((num_nodes, 1), float(current_time_sec), device=x.device, dtype=x.dtype)
            elif isinstance(current_time_sec, torch.Tensor):
                t_tensor = current_time_sec.to(device=x.device, dtype=x.dtype)
                if t_tensor.dim() == 0:
                    t_tensor = t_tensor.expand(num_nodes, 1)
                elif t_tensor.dim() == 1:
                    if t_tensor.size(0) == num_nodes:
                        t_tensor = t_tensor.unsqueeze(-1)
                    else:
                        t_tensor = t_tensor[0].expand(num_nodes, 1)
            else:
                t_tensor = torch.zeros((num_nodes, 1), device=x.device, dtype=x.dtype)
            t_emb = self.time2vec(t_tensor)
        else:
            t_emb = torch.zeros((num_nodes, self.time_dim), device=x.device, dtype=x.dtype)

        # 3. Spatio-Temporal Node Representation
        h_node = torch.cat([h_temp, h_delta, t_emb], dim=-1) # [N, hidden_dim*2 + time_dim]

        # 4. Spatial GATv2 Attention
        src, dst = edge_index[0], edge_index[1]
        h_src = self.lin_src(h_node).view(num_nodes, self.num_heads, self.hidden_dim)
        h_dst = self.lin_dst(h_node).view(num_nodes, self.num_heads, self.hidden_dim)

        alpha = F.leaky_relu(h_src[src] + h_dst[dst], negative_slope=0.2)
        score = (alpha * self.att).sum(dim=-1) # [E, num_heads]
        score_combined = self.out_proj(score).squeeze(-1) # [E]

        # 5. Tidal Movement Directional Bias conditioned on day of week
        if centripetal_scores is not None and current_time_sec is not None:
            if isinstance(centripetal_scores, torch.Tensor):
                c_scores = centripetal_scores.to(device=x.device, dtype=x.dtype)
            else:
                c_scores = torch.from_numpy(centripetal_scores).to(device=x.device, dtype=x.dtype)
            t_sec = float(current_time_sec) if isinstance(current_time_sec, (int, float)) else float(current_time_sec.mean().item())
            tidal_factor = get_tidal_bias(t_sec, day_of_week)
            score_combined = score_combined + (tidal_factor * c_scores[dst] * 1.5)

        # Normalized grouped softmax by source node
        exp_score = torch.exp(score_combined - score_combined.max())
        sum_exp = torch.zeros(num_nodes, device=x.device, dtype=x.dtype)
        sum_exp.scatter_add_(0, src, exp_score)

        denom = sum_exp[src] + 1e-6
        alpha_ij = exp_score / denom

        return alpha_ij
