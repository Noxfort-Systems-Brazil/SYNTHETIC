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
# File: src/physics/greenshields.py
# Author: Gabriel Moraes
# Date: 2026-10-06

from typing import Tuple
import numpy as np

class GreenshieldsModel:
    """
    Implements Greenshields fundamental diagram of traffic flow:
    v(rho) = v_free * (1 - rho / rho_jam)
    q(rho) = rho * v(rho)
    """

    @staticmethod
    def speed(density: np.ndarray, v_free: np.ndarray, rho_jam: np.ndarray) -> np.ndarray:
        """Computes speed in km/h from density (veh/km/lane)."""
        ratio = np.clip(density / np.maximum(rho_jam, 1e-3), 0.0, 1.0)
        return np.maximum(0.0, v_free * (1.0 - ratio))

    @staticmethod
    def flow(density: np.ndarray, v_free: np.ndarray, rho_jam: np.ndarray) -> np.ndarray:
        """Computes flow in veh/h from density."""
        speed = GreenshieldsModel.speed(density, v_free, rho_jam)
        return density * speed

    @staticmethod
    def demand_and_supply(density: np.ndarray, v_free: np.ndarray, rho_jam: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes Godunov Demand (Sending function D) and Supply (Receiving function S).
        Critical density rho_c = rho_jam / 2
        Capacity q_max = (rho_jam * v_free) / 4
        """
        rho_c = rho_jam * 0.5
        q_max = rho_c * (v_free * 0.5)
        current_flow = GreenshieldsModel.flow(density, v_free, rho_jam)

        demand = np.where(density <= rho_c, current_flow, q_max)
        supply = np.where(density <= rho_c, q_max, current_flow)

        return demand, supply
