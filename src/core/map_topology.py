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
# File: core/map_topology.py
# Author: Gabriel Moraes
# Date: 2026-08-16

from typing import Dict, List, Optional, Set, Tuple


class MapTopology:
    """
    Pure domain entity holding the spatial and topological representation of a road network.
    Stores coordinate nodes, navigable ways, road node references, and geographic bounds.
    """

    def __init__(self) -> None:
        self.nodes: Dict[str, Tuple[float, float]] = {}  # {node_id: (lat, lon)}
        self.ways: List[List[str]] = []  # list of lists of node IDs
        self.road_nodes: Set[str] = set()
        self.bounds: Optional[Tuple[float, float, float, float]] = None  # (min_lat, min_lon, max_lat, max_lon)

    def clear(self) -> None:
        """Resets all topological structures to empty."""
        self.nodes.clear()
        self.ways.clear()
        self.road_nodes.clear()
        self.bounds = None

    def is_empty(self) -> bool:
        """Returns True if the topology has no nodes or ways."""
        return len(self.nodes) == 0 and len(self.ways) == 0

    def add_node(self, node_id: str, lat: float, lon: float) -> None:
        """Registers or updates a geographic node."""
        self.nodes[node_id] = (lat, lon)

    def add_way(self, node_ids: List[str]) -> None:
        """Registers a road way sequence and updates the set of road nodes."""
        if len(node_ids) >= 2:
            self.ways.append(node_ids)
            self.road_nodes.update(node_ids)

    def update_bounds_from_nodes(self) -> None:
        """Calculates and updates bounding box if not explicitly set."""
        if not self.nodes:
            self.bounds = None
            return

        lats = [coord[0] for coord in self.nodes.values()]
        lons = [coord[1] for coord in self.nodes.values()]
        self.bounds = (min(lats), min(lons), max(lats), max(lons))
