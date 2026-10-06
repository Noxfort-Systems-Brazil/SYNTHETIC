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
# File: tests/test_pinn_hybrid.py
# Author: Gabriel Moraes
# Date: 2026-09-29

import unittest
import torch
import numpy as np

from src.models.vae_tcn import VAETCN, calculate_vae_loss
from src.models.deeponet import TrafficDeepONet, BranchNet, TrunkNet
from src.models.csdi_engine import CSDIBackbone
from src.algorithms.diffusion_process import DiffusionSampler
from src.agents.director import DirectorAgent
from src.services.physics_interpreter import TrafficPhysicsInterpreter


class TestPINNHybridArchitecture(unittest.TestCase):
    """
    Unit test suite for the Hybrid Physics-Informed Neural Architecture:
    1. PI-VAE (Physics-Informed VAE Loss & Constraints)
    2. PI-DeepONet (Branch/Trunk Operator & PDE Residual)
    3. PGDM (Physics-Guided Diffusion Models)
    4. Director Hybrid Pipeline End-to-End
    """

    def setUp(self):
        self.device = torch.device("cpu")
        self.batch_size = 2
        self.seq_len = 30
        self.cond_dim = 2048
        self.gat_dim = 32

    def test_pi_vae_loss_penalizes_physical_violations(self):
        """Test that PI-VAE loss penalizes data violating Greenshields or acceleration bounds."""
        # 1. Consistent traffic data: high flow -> low speed
        flow_valid = torch.linspace(0.2, 2.0, self.seq_len).unsqueeze(0).repeat(self.batch_size, 1)
        speed_valid = 1.0 - (flow_valid / 2.5)  # Follows Greenshields
        valid_traffic = torch.stack([flow_valid, speed_valid], dim=1)  # [B, 2, L]

        # 2. Inconsistent traffic data: negative flow and extreme speed spikes (jerk)
        flow_invalid = -torch.ones_like(flow_valid) * 1.5
        speed_invalid = torch.zeros_like(speed_valid)
        speed_invalid[:, ::2] = 2.5  # extreme oscillatory jerk
        invalid_traffic = torch.stack([flow_invalid, speed_invalid], dim=1)

        dummy_mu = torch.zeros(self.batch_size, 128)
        dummy_logvar = torch.zeros(self.batch_size, 128)

        _, _, _, phy_loss_valid = calculate_vae_loss(
            valid_traffic, valid_traffic, dummy_mu, dummy_logvar, lambda_physics=1.0
        )
        _, _, _, phy_loss_invalid = calculate_vae_loss(
            invalid_traffic, invalid_traffic, dummy_mu, dummy_logvar, lambda_physics=1.0
        )

        self.assertGreater(
            phy_loss_invalid.item(),
            phy_loss_valid.item(),
            "PI-VAE physics loss must be higher for physically invalid traffic states"
        )

    def test_deeponet_forward_and_pde_loss(self):
        """Test TrafficDeepONet forward pass shapes and PDE residual computation."""
        model = TrafficDeepONet(cond_dim=self.cond_dim, gat_dim=self.gat_dim, basis_dim=16).to(self.device)
        cond = torch.randn(self.batch_size, self.cond_dim, device=self.device)
        t_norm = torch.linspace(0.0, 1.0, self.seq_len, device=self.device).unsqueeze(-1)
        gat_emb = torch.randn(self.batch_size, self.gat_dim, device=self.device)

        out = model(cond, t_norm, gat_emb)
        self.assertEqual(out.shape, (self.batch_size, 2, self.seq_len))

        # Flow must be non-negative
        self.assertTrue(torch.all(out[:, 0, :] >= 0.0), "DeepONet flow must be non-negative")
        # Speed must be within reasonable physical bounds (10 to 120 km/h)
        self.assertTrue(torch.all(out[:, 1, :] >= 9.0), "DeepONet speed must exceed minimum clamp")
        self.assertTrue(torch.all(out[:, 1, :] <= 130.0), "DeepONet speed must be bounded")

        pde_loss = model.compute_pde_loss(cond, t_norm, gat_emb)
        self.assertTrue(torch.isfinite(pde_loss), "DeepONet PDE residual must be finite")
        self.assertGreater(pde_loss.item(), 0.0)

    def test_physics_guided_diffusion_generation(self):
        """Test that DiffusionSampler with physics_guidance=True executes cleanly and stays bounded."""
        model = CSDIBackbone(
            n_features=2,
            cond_dim=self.cond_dim,
            gat_dim=self.gat_dim,
            residual_channels=16,
            n_residual_layers=2,
            diffusion_steps=10
        ).to(self.device)

        sampler = DiffusionSampler(model, diffusion_steps=10)
        cond = torch.randn(1, self.cond_dim, device=self.device)
        gat_cond = torch.randn(1, self.gat_dim, device=self.device)

        # Generate with physics guidance active
        output_guided = sampler.generate(
            cond=cond,
            gat_cond=gat_cond,
            seq_len=self.seq_len,
            physics_guidance=True,
            guidance_scale=0.2
        )

        self.assertEqual(output_guided.shape, (1, 2, self.seq_len))
        self.assertFalse(torch.isnan(output_guided).any(), "PGDM output must not contain NaNs")
        self.assertFalse(torch.isinf(output_guided).any(), "PGDM output must not contain Infs")

    def test_director_hybrid_pipeline_action(self):
        """Test DirectorAgent executes with DeepONet prior, PI-VAE, and PGDM CSDI."""
        director = DirectorAgent()
        mock_script = {
            "scenario_vector": np.random.randn(2048).astype(np.float32).tolist(),
            "weather": "Clear"
        }
        steps = 15
        graph_emb = torch.randn(1, 32, device=director.device)

        result = director.action(mock_script, duration_steps=steps, graph_embedding=graph_emb)

        self.assertIn("vehicle_flow", result)
        self.assertIn("current_speed", result)
        self.assertEqual(len(result["vehicle_flow"]), steps)
        self.assertEqual(len(result["current_speed"]), steps)

        # Verify physics clamps
        for s in result["current_speed"]:
            self.assertGreaterEqual(s, 20)
            self.assertLessEqual(s, 110)
        for f in result["vehicle_flow"]:
            self.assertGreaterEqual(f, 0)


if __name__ == "__main__":
    unittest.main()
