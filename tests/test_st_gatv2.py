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
# File: tests/test_st_gatv2.py
# Author: Gabriel Moraes
# Date: 2026-10-06

import unittest
import torch
import numpy as np

from src.models.st_gatv2 import STGATv2, Time2Vec, get_tidal_bias
from src.models.pinn import PINN, PINNCorrector
from src.models.diffusion import Diffusion

class TestSTGATv2AndPINN(unittest.TestCase):
    def test_time2vec(self):
        t2v = Time2Vec(out_dim=16)
        tau = torch.tensor([0.0, 3600.0, 28800.0, 64800.0]) # 0h, 1h, 8h, 18h
        out = t2v(tau)
        self.assertEqual(out.shape, (4, 16))
        self.assertFalse(torch.isnan(out).any())

    def test_tidal_bias(self):
        # Morning weekday peak (8h) should have positive bias (towards city center)
        b_morning = get_tidal_bias(8.0 * 3600.0, day_of_week=0)
        self.assertGreater(b_morning, 0.5)

        # Evening weekday peak (18h) should have negative bias (towards suburbs)
        b_evening = get_tidal_bias(18.0 * 3600.0, day_of_week=0)
        self.assertLess(b_evening, -0.5)

    def test_st_gatv2_sliding_window(self):
        model = STGATv2(in_features=4, hidden_dim=32, num_heads=2, temporal_window=12)
        # N=5 nodes, T=12 time steps, F=4 features
        x = torch.randn(5, 12, 4)
        edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 3, 4]], dtype=torch.long)
        centripetal = torch.zeros(5)

        alphas = model(x, edge_index, current_time_sec=28800.0, centripetal_scores=centripetal, day_of_week=0)
        self.assertEqual(alphas.shape, (4,))
        self.assertTrue(torch.all(alphas >= 0.0))
        self.assertTrue(torch.all(alphas <= 1.0 + 1e-5))

    def test_pinn_zero_initialization(self):
        pinn = PINN(in_features=4, hidden_dim=32, max_correction_veh_h=50.0)
        x = torch.randn(10, 4)
        correction = pinn(x)
        # Prior to training, the output must be identically zero
        self.assertTrue(torch.all(correction == 0.0))

    def test_diffusion_forward(self):
        diff = Diffusion(in_features=4, hidden_dim=64, time_dim=32)
        x = torch.randn(5, 4)
        timesteps = torch.tensor([10.0, 20.0, 30.0, 40.0, 50.0])
        out = diff(x, timesteps)
        self.assertEqual(out.shape, (5, 1))
        self.assertTrue(torch.all(out >= -1.0))
        self.assertTrue(torch.all(out <= 1.0))

if __name__ == "__main__":
    unittest.main()
