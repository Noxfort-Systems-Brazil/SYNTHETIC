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
# File: src/models/pinn.py
# Author: Gabriel Moraes
# Date: 2026-10-06

import torch
import torch.nn as nn

class PINN(nn.Module):
    """
    Pure nn.Module Physics-Informed Neural Network (PINN).
    Infers non-equilibrium turbulence and higher-order flow adjustments.
    Stateless regarding simulation history.
    """

    def __init__(self, in_features: int = 4, hidden_dim: int = 32, max_correction_veh_h: float = 50.0):
        super().__init__()
        self.max_correction = max_correction_veh_h

        self.net = nn.Sequential(
            nn.Linear(in_features, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1),
            nn.Tanh() # Bounded in [-1.0, 1.0]
        )
        # Initialize output projection to zero so untrained network acts as pure physics identity
        nn.init.zeros_(self.net[4].weight)
        nn.init.zeros_(self.net[4].bias)


    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: [N, in_features]
        Returns: [N] flow correction delta_q in veh/h
        """
        raw = self.net(x).squeeze(-1)
        return raw * self.max_correction

# Backward compatibility alias
PINNCorrector = PINN
