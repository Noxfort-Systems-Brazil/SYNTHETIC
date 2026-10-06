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
# File: src/memory/sensor_memory.py
# Author: Gabriel Moraes
# Date: 2026-10-06

from dataclasses import dataclass
from typing import Dict, List
import numpy as np
from src.memory.topology_memory import TopologyMemory

@dataclass
class VirtualCamera:
    sensor_id: str
    edge_id: str
    edge_index: int
    lat: float
    lon: float
    num_lanes: int

@dataclass
class VirtualLoop:
    sensor_id: str
    edge_id: str
    edge_index: int
    lat: float
    lon: float
    lane: int

class SensorMemory:
    """
    Manages physical locations and registry of virtual sensors deployed across the city network.
    Decoupled from network emitters.
    """

    def __init__(self, topology: TopologyMemory, camera_ratio: float = 0.15, loop_ratio: float = 0.15):
        self.topology = topology
        self.cameras: List[VirtualCamera] = []
        self.loops: List[VirtualLoop] = []
        self.camera_map: Dict[str, VirtualCamera] = {}
        self.loop_map: Dict[str, VirtualLoop] = {}

        self._allocate_sensors(camera_ratio, loop_ratio)

    def _allocate_sensors(self, camera_ratio: float, loop_ratio: float):
        num_edges = self.topology.num_edges
        if num_edges == 0:
            return

        # Sort edges by capacity and length to place sensors in arterial roads
        importance = self.topology.capacities * self.topology.lengths_m
        ranked_indices = np.argsort(-importance)

        num_cameras = max(1, int(num_edges * camera_ratio))
        num_loops = max(1, int(num_edges * loop_ratio))

        # Deploy cameras on the highest importance edges
        for i in range(num_cameras):
            idx = int(ranked_indices[i])
            edge = self.topology.edges[idx]
            lat, lon = edge.mid_point
            cam_id = f"CAM_{edge.id}_{i+1:03d}"
            cam = VirtualCamera(
                sensor_id=cam_id,
                edge_id=edge.id,
                edge_index=idx,
                lat=lat,
                lon=lon,
                num_lanes=edge.num_lanes
            )
            self.cameras.append(cam)
            self.camera_map[cam_id] = cam

        # Deploy loops with offset ranking
        for i in range(num_loops):
            idx = int(ranked_indices[i % num_edges])
            edge = self.topology.edges[idx]
            lat, lon = edge.mid_point
            # Deploy a loop per lane or primary lane
            for lane_num in range(1, edge.num_lanes + 1):
                loop_id = f"LOOP_{edge.id}_L{lane_num}"
                loop = VirtualLoop(
                    sensor_id=loop_id,
                    edge_id=edge.id,
                    edge_index=idx,
                    lat=lat,
                    lon=lon,
                    lane=lane_num
                )
                self.loops.append(loop)
                self.loop_map[loop_id] = loop
