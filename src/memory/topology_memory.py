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
# File: src/memory/topology_memory.py
# Author: Gabriel Moraes
# Date: 2026-10-06

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import torch

from src.physics.centroid_analyzer import CentroidAnalyzer

@dataclass
class RoadEdge:
    id: str
    index: int
    from_node: str
    to_node: str
    num_lanes: int = 1
    length_m: float = 100.0
    speed_limit_kmh: float = 60.0
    capacity_veh_per_hour: float = 1800.0
    jam_density_veh_km: float = 140.0
    coordinates: List[Tuple[float, float]] = field(default_factory=list) # List of (lat, lon)
    shape: List[Tuple[float, float]] = field(default_factory=list) # List of (x, y) Cartesian points in meters
    name: str = ""
    edge_type: str = ""

    @property
    def speed_limit_mps(self) -> float:
        return self.speed_limit_kmh / 3.6

    @property
    def mid_point(self) -> Tuple[float, float]:
        if not self.coordinates:
            return (0.0, 0.0)
        mid_idx = len(self.coordinates) // 2
        return self.coordinates[mid_idx]


class TopologyMemory:
    """
    Decoupled representation of the static urban road topology.
    Contains strictly geometric and graph properties without neural network weights.
    """
    def __init__(
        self,
        edges: List[RoadEdge],
        connections: Optional[List[Tuple[str, str]]] = None,
        nodes: Optional[List[Dict[str, Any]]] = None,
        connection_signals: Optional[Dict[Tuple[str, str], Dict[str, Any]]] = None,
        tl_programs: Optional[Dict[str, Any]] = None
    ):
        self.edges = edges
        self.num_edges = len(edges)
        self.nodes = nodes or []
        self.connection_signals = connection_signals or {}
        self.tl_programs = tl_programs or {}
        self.edge_map: Dict[str, RoadEdge] = {e.id: e for e in edges}
        self.edge_id_to_index: Dict[str, int] = {e.id: e.index for e in edges}
        self.index_to_edge_id: Dict[int, str] = {e.index: e.id for e in edges}

        # Build incoming and outgoing adjacency
        self.outgoing: Dict[str, List[str]] = {e.id: [] for e in edges}
        self.incoming: Dict[str, List[str]] = {e.id: [] for e in edges}

        if connections:
            for src, dst in connections:
                if src in self.edge_map and dst in self.edge_map:
                    if dst not in self.outgoing[src]:
                        self.outgoing[src].append(dst)
                    if src not in self.incoming[dst]:
                        self.incoming[dst].append(src)
        else:
            # Infer connections through common nodes if explicit list not provided
            node_out: Dict[str, List[str]] = {}
            for e in edges:
                node_out.setdefault(e.from_node, []).append(e.id)
            for e in edges:
                for target_id in node_out.get(e.to_node, []):
                    if target_id != e.id:
                        self.outgoing[e.id].append(target_id)
                        self.incoming[target_id].append(e.id)

        # Identify boundary entry/exit edges
        self.inflow_edge_indices: List[int] = [e.index for e in edges if len(self.incoming[e.id]) == 0]
        self.outflow_edge_indices: List[int] = [e.index for e in edges if len(self.outgoing[e.id]) == 0]

        # In case graph is circular with no degree-0 nodes, fallback to highest capacity edges as entry points
        if not self.inflow_edge_indices and self.edges:
            self.inflow_edge_indices = [0]
        if not self.outflow_edge_indices and self.edges:
            self.outflow_edge_indices = [self.num_edges - 1]

        # Identify internal residential/local edges (interior streets with lower speed limit)
        self.internal_residential_indices: List[int] = [
            e.index for e in edges
            if e.index not in self.inflow_edge_indices
            and (e.speed_limit_kmh <= 45.0 or "residential" in getattr(e, "edge_type", "") or len(self.incoming[e.id]) == 1)
        ]

        # Compute geometric centroid and edge alignment vectors
        self.centroid, self.centripetal_scores = CentroidAnalyzer.analyze_network(self.edges)

        # Precompute vectorized numpy arrays
        self.lengths_m = np.array([e.length_m for e in edges], dtype=np.float32)
        self.speed_limits_kmh = np.array([e.speed_limit_kmh for e in edges], dtype=np.float32)
        self.num_lanes = np.array([e.num_lanes for e in edges], dtype=np.int32)
        self.capacities = np.array([e.capacity_veh_per_hour * e.num_lanes for e in edges], dtype=np.float32)
        self.jam_densities = np.array([e.jam_density_veh_km * e.num_lanes for e in edges], dtype=np.float32)

        # Precompute Graph Edge Index for PyTorch Geometric [2, E]
        src_indices = []
        dst_indices = []
        for src_id, targets in self.outgoing.items():
            src_idx = self.edge_id_to_index[src_id]
            for dst_id in targets:
                dst_idx = self.edge_id_to_index[dst_id]
                src_indices.append(src_idx)
                dst_indices.append(dst_idx)

        if src_indices:
            self.edge_index = torch.tensor([src_indices, dst_indices], dtype=torch.long)
        else:
            self.edge_index = torch.empty((2, 0), dtype=torch.long)

        # Compute geodetic bounding box
        all_coords = [pt for e in edges for pt in e.coordinates]
        if all_coords:
            lats = [pt[0] for pt in all_coords]
            lons = [pt[1] for pt in all_coords]
            self.min_lat, self.max_lat = min(lats), max(lats)
            self.min_lon, self.max_lon = min(lons), max(lons)
        else:
            self.min_lat, self.max_lat = -23.55, -23.50
            self.min_lon, self.max_lon = -46.65, -46.60

        # Compute Cartesian bounding box in meters
        all_shapes = [pt for e in edges for pt in e.shape]
        for n in self.nodes:
            all_shapes.append((n.get("x", 0.0), n.get("y", 0.0)))

        if all_shapes:
            xs = [pt[0] for pt in all_shapes]
            ys = [pt[1] for pt in all_shapes]
            self.min_x, self.max_x = min(xs), max(xs)
            self.min_y, self.max_y = min(ys), max(ys)
        else:
            self.min_x, self.max_x = 0.0, 1000.0
            self.min_y, self.max_y = 0.0, 1000.0

    def get_edge(self, edge_id: str) -> Optional[RoadEdge]:
        return self.edge_map.get(edge_id)

    def get_outgoing(self, edge_id: str) -> List[str]:
        return self.outgoing.get(edge_id, [])

    def get_incoming(self, edge_id: str) -> List[str]:
        return self.incoming.get(edge_id, [])

    @property
    def total_length_km(self) -> float:
        """Total length of all road links in kilometers."""
        if hasattr(self, "lengths_m") and len(self.lengths_m) > 0:
            return float(self.lengths_m.sum()) / 1000.0
        return sum(e.length_m for e in self.edges) / 1000.0

    @property
    def total_lane_length_km(self) -> float:
        """Total lane length across all edges in kilometers."""
        if hasattr(self, "lengths_m") and hasattr(self, "num_lanes") and len(self.lengths_m) > 0:
            return float((self.lengths_m * self.num_lanes).sum()) / 1000.0
        return sum(e.length_m * e.num_lanes for e in self.edges) / 1000.0

    @property
    def area_km2(self) -> float:
        """Approximate bounding box area of the road network in km²."""
        width_km = max(0.1, (self.max_x - self.min_x) / 1000.0)
        height_km = max(0.1, (self.max_y - self.min_y) / 1000.0)
        return float(width_km * height_km)

    @property
    def inferred_city_scale(self) -> str:
        """
        Infers city scale category from road network extent:
        - 'metropolis': Large urban network (>60km road, >30km² or >400 edges)
        - 'medium': Standard urban network (15-60km road, 6-30km² or 80-400 edges)
        - 'small': Neighborhood / small town (<15km road)
        """
        if self.total_length_km >= 60.0 or self.area_km2 >= 30.0 or self.num_edges >= 400:
            return "metropolis"
        elif self.total_length_km >= 15.0 or self.area_km2 >= 6.0 or self.num_edges >= 80:
            return "medium"
        else:
            return "small"

