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
# File: services/graph_converter.py
# Author: Gabriel Moraes
# Date: 2026-08-16

from typing import Dict, List, Tuple
import numpy as np

from src.core.map_topology import MapTopology


class GATv2GraphConverter:
    """
    Graph transformation service converting road network topology into standardized
    node feature matrices and bidirectional edge indices for GATv2 and GNN architectures.
    """

    @staticmethod
    def convert(topology: MapTopology) -> Tuple[np.ndarray, np.ndarray]:
        """
        Converts the parsed MapTopology into normalized Node Features and Edge Index.

        Returns:
            node_features: np.ndarray of shape (num_nodes, 2)
            edge_index: np.ndarray of shape (2, num_edges)
        """
        if not topology.road_nodes:
            return np.array([]), np.array([[], []])

        node_to_idx: Dict[str, int] = {}
        idx: int = 0
        for node_id in topology.road_nodes:
            if node_id in topology.nodes:
                node_to_idx[node_id] = idx
                idx += 1

        num_nodes: int = idx
        node_features: np.ndarray = np.zeros((num_nodes, 2), dtype=np.float32)

        for node_id, node_idx in node_to_idx.items():
            node_features[node_idx] = topology.nodes[node_id]

        if num_nodes > 0:
            mean_lat: float = float(np.mean(node_features[:, 0]))
            mean_lon: float = float(np.mean(node_features[:, 1]))
            node_features[:, 0] -= mean_lat
            node_features[:, 1] -= mean_lon
            max_val: float = float(np.max(np.abs(node_features)))
            if max_val > 0:
                node_features /= max_val

        src: List[int] = []
        dst: List[int] = []

        for way in topology.ways:
            for i in range(len(way) - 1):
                u = way[i]
                v = way[i + 1]

                if u in node_to_idx and v in node_to_idx:
                    u_idx = node_to_idx[u]
                    v_idx = node_to_idx[v]

                    src.append(u_idx)
                    dst.append(v_idx)
                    src.append(v_idx)
                    dst.append(u_idx)

        edge_index: np.ndarray = np.array([src, dst], dtype=np.int64)
        return node_features, edge_index
