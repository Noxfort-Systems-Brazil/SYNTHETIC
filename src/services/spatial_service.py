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
# File: services/spatial_service.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import math
from typing import Tuple

from src.core.map_topology import MapTopology


class SpatialService:
    """
    Spatial geometry service for distance calculations, coordinate projections,
    and snapping arbitrary geographic points to the nearest topological road segments.
    """

    @staticmethod
    def snap_to_road(lat: float, lon: float, topology: MapTopology) -> Tuple[float, float]:
        """
        Finds the closest point on any road segment within the topology to the given coordinates.
        Returns (lat, lon) unchanged if no road ways exist in the topology.
        """
        if not topology.ways:
            return lat, lon

        min_dist: float = float("inf")
        best_point: Tuple[float, float] = (lat, lon)

        lat_rad: float = math.radians(lat)
        lon_scale: float = math.cos(lat_rad)

        def dist_squared(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
            dy: float = p1[0] - p2[0]
            dx: float = (p1[1] - p2[1]) * lon_scale
            return dy**2 + dx**2

        def closest_point_on_segment(
            p: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]
        ) -> Tuple[float, float]:
            dy_ab: float = b[0] - a[0]
            dx_ab: float = (b[1] - a[1]) * lon_scale
            ab_len_sq: float = dy_ab**2 + dx_ab**2

            if ab_len_sq == 0:
                return a

            dy_ap: float = p[0] - a[0]
            dx_ap: float = (p[1] - a[1]) * lon_scale

            t: float = (dy_ap * dy_ab + dx_ap * dx_ab) / ab_len_sq
            t = max(0.0, min(1.0, t))

            return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))

        for way in topology.ways:
            for i in range(len(way) - 1):
                n1, n2 = way[i], way[i + 1]
                if n1 in topology.nodes and n2 in topology.nodes:
                    p1 = topology.nodes[n1]
                    p2 = topology.nodes[n2]

                    proj_p = closest_point_on_segment((lat, lon), p1, p2)
                    d_sq = dist_squared((lat, lon), proj_p)

                    if d_sq < min_dist:
                        min_dist = d_sq
                        best_point = proj_p

        return best_point
