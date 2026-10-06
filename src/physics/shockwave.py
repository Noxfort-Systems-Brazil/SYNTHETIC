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
# File: src/physics/shockwave.py
# Author: Gabriel Moraes
# Date: 2026-10-06

from typing import Tuple
import numpy as np

class ShockwaveAnalyzer:
    """
    Computes Rankine-Hugoniot shockwave jump conditions:
    w = (q2 - q1) / (rho2 - rho1)
    """

    @staticmethod
    def wave_speed(rho1: float, q1: float, rho2: float, q2: float) -> float:
        """
        Calculates propagation speed of the shockwave boundary in km/h.
        w < 0 implies wave travels upstream (backward shockwave).
        """
        delta_rho = rho2 - rho1
        if abs(delta_rho) < 1e-4:
            return 0.0
        return (q2 - q1) / delta_rho

    @staticmethod
    def detect_bottlenecks(
        densities: np.ndarray,
        flows: np.ndarray,
        speed_limits: np.ndarray,
        jam_densities: np.ndarray
    ) -> np.ndarray:
        """
        Returns boolean mask indicating edges experiencing severe backward shockwaves (jams).
        """
        occ_ratio = densities / np.maximum(jam_densities, 1.0)
        return occ_ratio > 0.65
