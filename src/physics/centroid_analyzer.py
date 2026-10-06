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
# File: src/physics/centroid_analyzer.py
# Author: Gabriel Moraes
# Date: 2026-10-06

import math
from typing import List, Tuple
import numpy as np

class CentroidAnalyzer:
    """
    Computes the geometric centroid of the road network and determines
    for each edge whether its orientation is centripetal (pointing towards center, +1)
    or centrifugal (pointing towards outskirts/suburbs, -1).
    """

    @staticmethod
    def analyze_network(edges: List) -> Tuple[Tuple[float, float], np.ndarray]:
        """
        Calculates network centroid (X, Y) in Cartesian coordinates
        and returns an array of centripetal alignment scores in [-1.0, 1.0] for all edges.
        """
        num_edges = len(edges)
        if num_edges == 0:
            return (0.0, 0.0), np.zeros(0, dtype=np.float32)

        # 1. Compute weighted center of mass
        total_weight = 0.0
        sum_x = 0.0
        sum_y = 0.0

        edge_midpoints = []
        edge_vectors = []

        for edge in edges:
            length = getattr(edge, "length_m", 100.0)
            shape = getattr(edge, "shape", [])

            if shape and len(shape) >= 2:
                p_start = shape[0]
                p_end = shape[-1]
                mid_idx = len(shape) // 2
                p_mid = shape[mid_idx]
                vx = p_end[0] - p_start[0]
                vy = p_end[1] - p_start[1]
            elif shape and len(shape) == 1:
                p_mid = shape[0]
                vx = 0.0
                vy = 0.0
            else:
                p_mid = (0.0, 0.0)
                vx = 0.0
                vy = 0.0

            edge_midpoints.append(p_mid)
            edge_vectors.append((vx, vy))

            w = max(10.0, length)
            sum_x += p_mid[0] * w
            sum_y += p_mid[1] * w
            total_weight += w

        cx = sum_x / total_weight if total_weight > 0 else 0.0
        cy = sum_y / total_weight if total_weight > 0 else 0.0
        centroid = (cx, cy)

        # 2. Compute directional cosine with centroid vector
        scores = np.zeros(num_edges, dtype=np.float32)
        for i in range(num_edges):
            mx, my = edge_midpoints[i]
            vx, vy = edge_vectors[i]

            # Vector pointing towards centroid
            dx = cx - mx
            dy = cy - my

            mag_v = math.sqrt(vx * vx + vy * vy)
            mag_d = math.sqrt(dx * dx + dy * dy)

            if mag_v < 1e-4 or mag_d < 1e-4:
                scores[i] = 0.0
            else:
                cos_theta = (vx * dx + vy * dy) / (mag_v * mag_d)
                scores[i] = float(np.clip(cos_theta, -1.0, 1.0))

        return centroid, scores
