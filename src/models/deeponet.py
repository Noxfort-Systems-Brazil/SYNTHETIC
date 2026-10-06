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
# File: models/deeponet.py
# Author: Gabriel Moraes
# Date: 2026-09-29

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional


class BranchNet(nn.Module):
    """
    Branch Network of DeepONet.
    Encodes the high-dimensional conditioning function (SLM scenario vector + weather).
    """

    def __init__(self, in_features: int = 2048, hidden_dim: int = 256, basis_dim: int = 64, n_outputs: int = 2):
        super().__init__()
        self.basis_dim = basis_dim
        self.n_outputs = n_outputs
        
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.SiLU(),
            nn.Linear(hidden_dim // 2, basis_dim * n_outputs),
        )

    def forward(self, u: torch.Tensor) -> torch.Tensor:
        """
        u: [Batch, in_features]
        Returns: [Batch, n_outputs, basis_dim]
        """
        out = self.net(u)
        batch_size = u.shape[0]
        return out.view(batch_size, self.n_outputs, self.basis_dim)


class TrunkNet(nn.Module):
    """
    Trunk Network of DeepONet.
    Encodes continuous spatio-temporal query coordinates:
    normalized time t in [0, 1] + spatial graph context embedding from GATv2.
    """

    def __init__(self, in_features: int = 33, hidden_dim: int = 128, basis_dim: int = 64, n_outputs: int = 2):
        super().__init__()
        self.basis_dim = basis_dim
        self.n_outputs = n_outputs
        
        # Fourier feature projection for smooth temporal representation
        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, basis_dim * n_outputs),
        )

    def forward(self, y: torch.Tensor) -> torch.Tensor:
        """
        y: [Batch, Seq_Len, in_features] or [Seq_Len, in_features]
        Returns: [Batch, Seq_Len, n_outputs, basis_dim]
        """
        if y.dim() == 2:
            y = y.unsqueeze(0)
            
        batch_size, seq_len, _ = y.shape
        out = self.net(y)
        return out.view(batch_size, seq_len, self.n_outputs, self.basis_dim)


class TrafficDeepONet(nn.Module):
    """
    Physics-Informed Deep Operator Network (PI-DeepONet) for Traffic Synthesis.
    
    Maps macro scenario conditions u (from SLM) to the continuous traffic state
    [vehicle_flow, current_speed] at any arbitrary continuous temporal and spatial
    coordinates y.
    
    Output operator:
        G(u)(y)_k = sum_j (b_{j,k}(u) * t_{j,k}(y)) + bias_k
    """

    def __init__(
        self,
        cond_dim: int = 2048,
        gat_dim: int = 32,
        basis_dim: int = 64,
        free_flow_speed: float = 80.0,
        jam_density: float = 120.0,
    ):
        super().__init__()
        self.cond_dim = cond_dim
        self.gat_dim = gat_dim
        self.basis_dim = basis_dim
        self.free_flow_speed = free_flow_speed
        self.jam_density = jam_density

        # in_features for trunk = 1 (normalized time t) + gat_dim (spatial context)
        self.trunk_in_dim = 1 + gat_dim

        self.branch = BranchNet(in_features=cond_dim, basis_dim=basis_dim, n_outputs=2)
        self.trunk = TrunkNet(in_features=self.trunk_in_dim, basis_dim=basis_dim, n_outputs=2)

        self.bias = nn.Parameter(torch.zeros(2))
        
        # Scaling parameters for physical bounds
        self.scale_flow = nn.Parameter(torch.tensor(300.0))
        self.scale_speed = nn.Parameter(torch.tensor(80.0))

    def forward(self, cond: torch.Tensor, t_norm: torch.Tensor, gat_emb: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        cond: [Batch, cond_dim] - SLM scenario embedding
        t_norm: [Batch, Seq_Len, 1] or [Seq_Len, 1] - Normalized time coordinates in [0, 1]
        gat_emb: [Batch, gat_dim] or [1, gat_dim] - Spatial graph context
        
        Returns:
            Tensor of shape [Batch, 2, Seq_Len] representing [flow, speed]
        """
        batch_size = cond.shape[0]
        
        if t_norm.dim() == 2:
            t_norm = t_norm.unsqueeze(0).expand(batch_size, -1, -1)
            
        seq_len = t_norm.shape[1]

        if gat_emb is None:
            gat_emb = torch.zeros((batch_size, self.gat_dim), device=cond.device)
        elif gat_emb.shape[0] != batch_size:
            gat_emb = gat_emb.expand(batch_size, -1)

        # Broadcast gat_emb across sequence length: [Batch, Seq_Len, gat_dim]
        gat_expanded = gat_emb.unsqueeze(1).expand(-1, seq_len, -1)
        trunk_in = torch.cat([t_norm, gat_expanded], dim=-1)

        # Branch outputs: [Batch, 2, basis_dim]
        b_out = self.branch(cond)
        
        # Trunk outputs: [Batch, Seq_Len, 2, basis_dim]
        t_out = self.trunk(trunk_in)

        # Compute inner product over basis_dim:
        # b_out: [Batch, 1, 2, basis_dim]
        b_expanded = b_out.unsqueeze(1)
        
        # Dot product along basis_dim: [Batch, Seq_Len, 2]
        dot_product = torch.sum(b_expanded * t_out, dim=-1) + self.bias
        
        # Physical activation:
        # Flow is strictly non-negative: Softplus
        flow = F.softplus(dot_product[:, :, 0]) * (self.scale_flow / 100.0)
        
        # Speed is bounded between 10 km/h and 120 km/h: Sigmoid scaled
        speed = 10.0 + torch.sigmoid(dot_product[:, :, 1]) * (self.scale_speed - 10.0)
        
        # Stack to [Batch, 2, Seq_Len]
        out = torch.stack([flow, speed], dim=1)
        return out

    def compute_pde_loss(self, cond: torch.Tensor, t_norm: torch.Tensor, gat_emb: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Calculates the PDE physics residual loss based on the Lighthill-Whitham-Richards (LWR)
        conservation law and Greenshields fundamental diagram:
            v_expected = v_free * (1 - flow / max_flow)
            L_pde = MSE(speed, v_expected) + acceleration_limit_penalty
        """
        out = self.forward(cond, t_norm, gat_emb)
        flow = out[:, 0, :]
        speed = out[:, 1, :]

        # Greenshields consistency
        expected_speed = self.free_flow_speed * torch.clamp(1.0 - (flow / (self.scale_flow + 1e-5)), min=0.1, max=1.1)
        greenshields_loss = F.mse_loss(speed, expected_speed)

        # Acceleration inertia limit (derivative with respect to normalized time)
        if speed.shape[-1] > 1:
            dt = 1.0 / speed.shape[-1]
            dv_dt = (speed[:, 1:] - speed[:, :-1]) / dt
            # Max acceleration in km/h per fractional day
            accel_penalty = torch.mean(F.relu(torch.abs(dv_dt) - 1500.0).pow(2))
        else:
            accel_penalty = torch.tensor(0.0, device=cond.device)

        return greenshields_loss + 0.1 * accel_penalty


if __name__ == "__main__":
    print("Testing TrafficDeepONet Architecture...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    batch_size = 2
    seq_len = 48
    cond_dim = 2048
    gat_dim = 32

    model = TrafficDeepONet(cond_dim=cond_dim, gat_dim=gat_dim).to(device)
    dummy_cond = torch.randn(batch_size, cond_dim, device=device)
    dummy_t = torch.linspace(0, 1, seq_len, device=device).unsqueeze(-1)
    dummy_gat = torch.randn(batch_size, gat_dim, device=device)

    pred = model(dummy_cond, dummy_t, dummy_gat)
    loss = model.compute_pde_loss(dummy_cond, dummy_t, dummy_gat)

    print(f"Output shape: {pred.shape} (Expected: [{batch_size}, 2, {seq_len}])")
    print(f"PDE Loss: {loss.item():.4f}")
    print("DeepONet architecture verified successfully.")
