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
# File: tests/test_gatv2.py
# Author: Gabriel Moraes
# Date: 2026-09-29

import unittest
from unittest.mock import MagicMock, patch
import torch
import numpy as np

from src.models.gatv2 import LightweightGATv2


class TestLightweightGATv2(unittest.TestCase):
    def setUp(self):
        self.gat = LightweightGATv2(in_channels=2, hidden_channels=16, out_channels=32, heads=2)

    def test_forward_pass_single_graph(self):
        # 5 nodes with (lat, lon) features
        x = torch.randn(5, 2, dtype=torch.float32)
        # Undirected edge index for 5 nodes: 0-1, 1-2, 2-3, 3-4
        edge_index = torch.tensor([
            [0, 1, 1, 2, 2, 3, 3, 4, 1, 0, 2, 1, 3, 2, 4, 3],
            [1, 0, 2, 1, 3, 2, 4, 3, 0, 1, 1, 2, 2, 3, 3, 4]
        ], dtype=torch.long)

        out = self.gat(x, edge_index)
        self.assertEqual(out.shape, (1, 32))
        self.assertFalse(torch.isnan(out).any())

    def test_forward_pass_batch_graphs(self):
        # 6 nodes across 2 graphs (graph 0 has nodes 0,1,2; graph 1 has nodes 3,4,5)
        x = torch.randn(6, 2, dtype=torch.float32)
        edge_index = torch.tensor([
            [0, 1, 1, 2, 3, 4, 4, 5],
            [1, 0, 2, 1, 4, 3, 5, 4]
        ], dtype=torch.long)
        batch = torch.tensor([0, 0, 0, 1, 1, 1], dtype=torch.long)

        out = self.gat(x, edge_index, batch=batch)
        self.assertEqual(out.shape, (2, 32))
        self.assertFalse(torch.isnan(out).any())

    def test_extract_context_with_valid_map(self):
        mock_map_provider = MagicMock()
        mock_map_provider.parse_osm_to_graph.return_value = (
            np.array([[ -23.5, -51.2], [-23.51, -51.21]], dtype=np.float32),
            np.array([[0, 1], [1, 0]], dtype=np.int64)
        )

        embedding = self.gat.extract_context(mock_map_provider)
        self.assertEqual(embedding.shape, (1, 32))
        self.assertIsInstance(embedding, torch.Tensor)

    def test_extract_context_empty_map_fallback(self):
        mock_map_provider = MagicMock()
        mock_map_provider.parse_osm_to_graph.return_value = (
            np.array([], dtype=np.float32),
            np.array([], dtype=np.int64)
        )

        embedding = self.gat.extract_context(mock_map_provider)
        self.assertEqual(embedding.shape, (1, 32))
        self.assertTrue((embedding == 0).all())

    def test_gatv2_missing_dependency_raises_import_error(self):
        with patch("src.models.gatv2.GATv2Conv", None):
            with self.assertRaises(ImportError):
                LightweightGATv2()


if __name__ == "__main__":
    unittest.main()
