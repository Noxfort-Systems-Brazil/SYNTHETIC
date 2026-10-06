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
# File: src/memory/spatiotemporal_memory.py
# Author: Gabriel Moraes
# Date: 2026-10-06

from typing import Tuple
import numpy as np
import torch

class SpatioTemporalMemory:
    """
    Decoupled state buffer managing historical sliding window tensors [N, T, F].
    Stateless regarding neural weights.
    
    Features:
    0: Density rho (veh/km/lane)
    1: Speed v (km/h)
    2: Flow q (veh/h)
    3: Occupancy ratio (0.0 to 1.0)
    """

    def __init__(self, num_edges: int, window_size: int = 12):
        self.num_edges = num_edges
        self.window_size = window_size
        self.num_features = 4

        # Initialize buffer [N, T, F]
        self._buffer = np.zeros((num_edges, window_size, self.num_features), dtype=np.float32)
        self.step_count = 0

    def initialize_state(self, initial_densities: np.ndarray, speed_limits: np.ndarray):
        """Initializes the window with baseline equilibrium values."""
        densities = np.clip(initial_densities, 0.0, 140.0)
        speeds = np.clip(speed_limits * (1.0 - densities / 140.0), 5.0, 120.0)
        flows = densities * speeds
        occupancies = np.clip(densities / 140.0, 0.0, 1.0)

        for t in range(self.window_size):
            self._buffer[:, t, 0] = densities
            self._buffer[:, t, 1] = speeds
            self._buffer[:, t, 2] = flows
            self._buffer[:, t, 3] = occupancies

    def push_step(self, densities: np.ndarray, speeds: np.ndarray, flows: np.ndarray, occupancies: np.ndarray):
        """Rolls the sliding window by 1 step and inserts the current step snapshot."""
        # Shift along time axis
        self._buffer[:, :-1, :] = self._buffer[:, 1:, :]

        # Insert new step at index -1
        self._buffer[:, -1, 0] = np.nan_to_num(densities, nan=0.0)
        self._buffer[:, -1, 1] = np.nan_to_num(speeds, nan=0.0)
        self._buffer[:, -1, 2] = np.nan_to_num(flows, nan=0.0)
        self._buffer[:, -1, 3] = np.clip(np.nan_to_num(occupancies, nan=0.0), 0.0, 1.0)

        self.step_count += 1

    def get_current_slice(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Returns the latest step values (densities, speeds, flows, occupancies)."""
        latest = self._buffer[:, -1, :]
        return latest[:, 0], latest[:, 1], latest[:, 2], latest[:, 3]

    def get_tensor_window(self, device: torch.device) -> torch.Tensor:
        """Returns PyTorch tensor [N, T, F] on the requested device."""
        return torch.from_numpy(self._buffer).to(device=device, dtype=torch.float32)

    def get_latest_tensor(self, device: torch.device) -> torch.Tensor:
        """Returns PyTorch tensor [N, F] for the latest step."""
        return torch.from_numpy(self._buffer[:, -1, :]).to(device=device, dtype=torch.float32)
