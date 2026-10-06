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
# File: diffusion_process.py
# Author: Gabriel Moraes
# Date: 2026-06-04

import torch
import torch.nn.functional as F

class DiffusionSampler:
    """
    Responsibility: Handle Denoising Diffusion Probabilistic Models (DDPM) math.
    Encapsulates the noise schedule, loss computation, and generation (reverse sampling).
    """

    def __init__(self, model: torch.nn.Module, diffusion_steps: int = 50):
        self.model = model
        self.diffusion_steps = diffusion_steps
        self.device = next(model.parameters()).device

        # --- Noise Schedule (Linear Beta Schedule) ---
        betas = torch.linspace(1e-4, 0.02, diffusion_steps, device=self.device)
        alphas = 1.0 - betas
        alphas_cumprod = torch.cumprod(alphas, dim=0)

        self.betas = betas
        self.alphas = alphas
        self.alphas_cumprod = alphas_cumprod
        self.sqrt_alphas_cumprod = torch.sqrt(alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1.0 - alphas_cumprod)

    def compute_loss(self, x_0: torch.Tensor, cond: torch.Tensor, gat_cond: torch.Tensor) -> torch.Tensor:
        """
        Computes the simplified DDPM training loss (MSE between true and predicted noise).
        """
        batch_size = x_0.shape[0]

        # Sample random timesteps
        t = torch.randint(0, self.diffusion_steps, (batch_size,), device=x_0.device)

        # Sample noise
        noise = torch.randn_like(x_0)

        # Create noisy version: x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * noise
        sqrt_alpha = self.sqrt_alphas_cumprod[t].view(-1, 1, 1)
        sqrt_one_minus = self.sqrt_one_minus_alphas_cumprod[t].view(-1, 1, 1)
        x_noisy = sqrt_alpha * x_0 + sqrt_one_minus * noise

        # Predict noise
        device_type = 'cuda' if x_0.is_cuda else 'cpu'
        with torch.autocast(device_type=device_type, enabled=(device_type == 'cuda')):
            noise_pred = self.model(x_noisy, cond, gat_cond, t)
            loss = F.mse_loss(noise_pred, noise)

        return loss

    def generate(
        self,
        cond: torch.Tensor,
        gat_cond: torch.Tensor,
        seq_len: int,
        n_steps: int = None,
        seed_tail: torch.Tensor = None,
        seed_alpha: float = 0.6,
        physics_guidance: bool = True,
        guidance_scale: float = 0.15,
    ) -> torch.Tensor:
        """
        Generates time-series data from pure Gaussian noise via iterative denoising.
        Supports inter-day context seeding and Physics-Guided Diffusion (PGDM) steering.
        """
        steps = n_steps or self.diffusion_steps
        batch_size = cond.shape[0]

        with torch.no_grad():
            # Start from pure noise
            x = torch.randn(batch_size, self.model.n_features, seq_len, device=cond.device)

            # Context Seeding: inject previous day's tail into the noise
            if seed_tail is not None:
                seed_tail = seed_tail.to(cond.device)
                tail_len = min(seed_tail.shape[-1], seq_len)
                noise_scale = self.sqrt_one_minus_alphas_cumprod[-1]
                noisy_tail = seed_tail[:, :, -tail_len:] + noise_scale * torch.randn_like(seed_tail[:, :, -tail_len:])
                x[:, :, :tail_len] = (seed_alpha * noisy_tail + (1 - seed_alpha) * x[:, :, :tail_len])

            for i in reversed(range(steps)):
                t = torch.full((batch_size,), i, dtype=torch.long, device=cond.device)

                # Predict noise
                device_type = 'cuda' if x.is_cuda else 'cpu'
                with torch.autocast(device_type=device_type, enabled=(device_type == 'cuda')):
                    noise_pred = self.model(x, cond, gat_cond, t)

                # DDPM update rule
                alpha_t = self.alphas[i]
                alpha_bar_t = self.alphas_cumprod[i]
                beta_t = self.betas[i]

                coeff = beta_t / torch.sqrt(1.0 - alpha_bar_t)
                mu = (1.0 / torch.sqrt(alpha_t)) * (x - coeff * noise_pred)

                # Physics Guidance (PGDM): Steer reverse sampling using LWR / Greenshields gradients
                if physics_guidance and guidance_scale > 0.0 and self.model.n_features >= 2:
                    with torch.enable_grad():
                        # Tweedie's formula estimate for clean state x_0
                        x_0_hat = (x - torch.sqrt(1.0 - alpha_bar_t) * noise_pred) / torch.sqrt(alpha_bar_t)
                        x_0_hat = x_0_hat.detach().requires_grad_(True)

                        flow = x_0_hat[:, 0, :]
                        speed = x_0_hat[:, 1, :]

                        # 1. Non-negativity / bounding loss
                        loss_neg = torch.mean(F.relu(-flow).pow(2) + F.relu(-speed - 1.0).pow(2))

                        # 2. Greenshields negative correlation in normalized diffusion space
                        expected_speed = -0.5 * flow
                        loss_greenshields = F.mse_loss(speed, expected_speed)

                        # 3. Jerk/Smoothness constraint
                        if speed.shape[-1] > 2:
                            jerk = speed[:, 2:] - 2 * speed[:, 1:-1] + speed[:, :-2]
                            loss_jerk = torch.mean(jerk.pow(2))
                        else:
                            loss_jerk = torch.tensor(0.0, device=x.device)

                        physics_loss = loss_greenshields + 0.3 * loss_jerk + loss_neg
                        grad_phy = torch.autograd.grad(physics_loss, x_0_hat)[0]

                    # Steer mean using physics gradient
                    step_guidance = guidance_scale * beta_t
                    mu = mu - step_guidance * grad_phy.detach()

                # Add noise for all steps except the last
                if i > 0:
                    sigma = torch.sqrt(beta_t)
                    x = mu + sigma * torch.randn_like(x)
                else:
                    x = mu

            return x
