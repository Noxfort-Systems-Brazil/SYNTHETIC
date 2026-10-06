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
# File: src/physics/geo_projection.py
# Author: Gabriel Moraes
# Date: 2026-10-06

from typing import Tuple

class GeoProjection:
    """
    Handles coordinate projection and interpolation between
    SUMO Cartesian coordinates (meters) and WGS84 geodetic coordinates (Lat, Lon).
    """

    def __init__(
        self,
        conv_bounds: Tuple[float, float, float, float] = (0.0, 0.0, 1000.0, 1000.0),
        orig_bounds: Tuple[float, float, float, float] = (-46.65, -23.55, -46.60, -23.50)
    ) -> None:
        self.cx1, self.cy1, self.cx2, self.cy2 = conv_bounds
        self.o_lon1, self.o_lat1, self.o_lon2, self.o_lat2 = orig_bounds

    @classmethod
    def from_sumo_location(cls, conv_str: str, orig_str: str) -> "GeoProjection":
        """Instantiates projection boundaries from SUMO convBoundary and origBoundary strings."""
        conv_bounds = (0.0, 0.0, 1000.0, 1000.0)
        orig_bounds = (-46.65, -23.55, -46.60, -23.50)

        if conv_str:
            try:
                parts = [float(p) for p in conv_str.split(",")]
                if len(parts) == 4:
                    conv_bounds = tuple(parts)
            except (ValueError, TypeError):
                pass

        if orig_str:
            try:
                parts = [float(p) for p in orig_str.split(",")]
                if len(parts) == 4:
                    orig_bounds = tuple(parts)
            except (ValueError, TypeError):
                pass

        return cls(conv_bounds=conv_bounds, orig_bounds=orig_bounds)

    def xy_to_latlon(self, x: float, y: float) -> Tuple[float, float]:
        """
        Converts Cartesian (x, y) coordinates to geodetic (lat, lon) coordinates
        via bi-linear bounding interpolation.
        """
        dx = self.cx2 - self.cx1 if abs(self.cx2 - self.cx1) > 1e-5 else 1.0
        dy = self.cy2 - self.cy1 if abs(self.cy2 - self.cy1) > 1e-5 else 1.0
        u = (x - self.cx1) / dx
        v = (y - self.cy1) / dy
        lon = self.o_lon1 + u * (self.o_lon2 - self.o_lon1)
        lat = self.o_lat1 + v * (self.o_lat2 - self.o_lat1)
        return (lat, lon)
