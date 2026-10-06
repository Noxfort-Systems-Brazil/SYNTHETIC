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
# File: models/slm_engine.py
# Author: Gabriel Moraes
# Date: 2026-02-26

import gc
import os
import re
import sys
import json
from typing import Optional, Dict, Any
import numpy as np

from src.core.logger import logger
from src.core.telemetry import HardwareTelemetry

try:
    import src.core.cuda_loader  # noqa: F401
except Exception:
    pass

# Attempt to import the inference library
try:
    from llama_cpp import Llama
except (ImportError, RuntimeError, OSError) as e:
    logger.critical(f"llama-cpp-python failed to load: {e}. Please run: pip install llama-cpp-python nvidia-cuda-runtime-cu12 nvidia-cublas-cu12")
    sys.exit(1)

class SLMEngine:
    """
    Wrapper class for the Small Language Model (GGUF) optimized for Vector output.
    Focuses on extracting semantic embeddings (Latent Vectors) rather than just text,
    with prompts, directives, and hyperparameters externalized to JSON for OCP compliance.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        n_ctx: Optional[int] = None,
        n_gpu_layers: Optional[int] = None,
        temperature: Optional[float] = None,
        config_path: Optional[str] = None
    ) -> None:
        """
        Initializes the inference engine with Embedding support enabled.
        Configurable via JSON and optional constructor overrides.
        """
        if config_path is None:
            base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "prompt", "slm_engine.json")
        self.config: Dict[str, Any] = self._load_config(config_path)

        model_cfg: Dict[str, Any] = self.config.get("model_config", {})
        
        self.temperature: float = temperature if temperature is not None else model_cfg.get("temperature", 0.85)
        ctx_capacity: int = n_ctx if n_ctx is not None else model_cfg.get("n_ctx", 8192)
        gpu_layers: int = n_gpu_layers if n_gpu_layers is not None else model_cfg.get("n_gpu_layers", 0)
        is_verbose: bool = model_cfg.get("verbose", False)
        enable_embedding: bool = model_cfg.get("embedding", True)

        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rel_path = model_cfg.get("default_model_relative_path", ["models", "vault", "Phi-4-mini-reasoning-UD-Q6_K_XL.gguf"])
            self.model_path: str = os.path.join(base_dir, *rel_path)
        else:
            self.model_path = model_path

        if not os.path.exists(self.model_path):
            error_hint = self.config.get("error_messages", {}).get(
                "model_not_found_hint",
                "Please verify model path or place the required GGUF weights into the models/vault/ directory."
            )
            raise FileNotFoundError(
                f"[SLMEngine] Model file not found at: {self.model_path}\n{error_hint}"
            )

        logger.info(f"[SLMEngine] Loading model for Vector Synthesis from: {self.model_path}...")
        logger.info(f"[SLMEngine] Context Window Capacity: {ctx_capacity} tokens.")

        try:
            self.llm: Optional[Llama] = Llama(
                model_path=self.model_path,
                n_ctx=ctx_capacity,
                n_gpu_layers=gpu_layers,
                verbose=is_verbose,
                embedding=enable_embedding
            )
            logger.info("[SLMEngine] Vector Engine loaded successfully.")
            
            # Start hardware telemetry from config settings
            telemetry_cfg: Dict[str, Any] = self.config.get("telemetry", {})
            log_file = telemetry_cfg.get("log_filename", "synthetic_slm.log")
            interval = telemetry_cfg.get("interval_sec", 2)
            
            self.telemetry = HardwareTelemetry(log_filename=log_file, interval_sec=interval)
            self.telemetry.start()
            
        except Exception as e:
            raise RuntimeError(f"[SLMEngine] Failed to initialize Llama context: {e}") from e

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Loads SLM engine configuration and prompt directives from JSON."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"[SLMEngine] Config file not found or inaccessible at '{path}': {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"[SLMEngine] Config file corrupted at '{path}': {e}")
            return {}

    def dream_daily_scenario(self, system_instruction: str, user_prompt: str) -> Dict[str, Any]:
        """
        Generates a creative scenario internally (Transient Memory) and returns both
        its numerical vector representation (Embedding) and the generated scenario payload.
        """
        prompts_cfg: Dict[str, Any] = self.config.get("prompts", {})
        model_cfg: Dict[str, Any] = self.config.get("model_config", {})

        # Injecting the Cognitive Directive to force Chain-of-Thought (Thinking Mode)
        cognitive_directive = prompts_cfg.get(
            "cognitive_directive",
            self.config.get("cognitive_directive", "")
        )
        cognitive_instruction: str = (
            f"{system_instruction}\n\n{cognitive_directive}" if cognitive_directive else system_instruction
        )

        messages: list = [
            {"role": "system", "content": cognitive_instruction},
            {"role": "user", "content": user_prompt}
        ]
        
        latent_dim: int = model_cfg.get("latent_dim", self.config.get("latent_dim", 2048))
        max_tokens: int = model_cfg.get("max_tokens", self.config.get("max_tokens", 1024))

        try:
            assert self.llm is not None
            completion = self.llm.create_chat_completion(
                messages=messages,
                temperature=self.temperature, 
                max_tokens=max_tokens
            )
            dream_text: str = completion['choices'][0]['message']['content']
            
            # Strip <think>...</think> for display — thinking is internal only
            thinking_regex = prompts_cfg.get("thinking_tag_regex", r'<think>.*?</think>')
            visible_text: str = re.sub(thinking_regex, '', dream_text, flags=re.DOTALL).strip()
            fallback_display = prompts_cfg.get(
                "fallback_scenario_display",
                "[Thinking mode active — scenario encoded directly]"
            )
            
            logger.info("\n" + "="*50)
            logger.info("Scenario Description:")
            logger.info("-" * 50)
            logger.info(visible_text if visible_text else fallback_display)
            logger.info("="*50 + "\n")
            
            # 2. Convert the Dream (Thoughts + Scenario) to a Vector (Embedding)
            logger.info("[SLMEngine] Converting thoughts into Latent Vector...")
            embedding_response = self.llm.create_embedding(dream_text)
            
            # Extract the raw vector list
            raw_vector = embedding_response['data'][0]['embedding']
            
            # Latent dimension target (keeping latent_dim for CSDI compatibility)
            vector: list
            
            # Robust Mean Pooling to handle variable llama.cpp output structures
            if isinstance(raw_vector[0], list):
                logger.info(f"[SLMEngine] Nested token embeddings detected. Pooling {len(raw_vector)} tokens...")
                vector_matrix = np.array(raw_vector)
                vector = vector_matrix.mean(axis=0).tolist()
            else:
                if len(raw_vector) > latent_dim and len(raw_vector) % latent_dim == 0:
                    logger.info(f"[SLMEngine] Flat token embeddings detected. Pooling...")
                    num_tokens = len(raw_vector) // latent_dim
                    vector_matrix = np.array(raw_vector).reshape(num_tokens, latent_dim)
                    vector = vector_matrix.mean(axis=0).tolist()
                else:
                    vector = raw_vector[:latent_dim]
            
            # Failsafe padding or truncation just to guarantee the exact shape for VAE-TCN
            if len(vector) < latent_dim:
                vector = vector + [0.0] * (latent_dim - len(vector))
            elif len(vector) > latent_dim:
                vector = vector[:latent_dim]
            
            return {
                "vector": vector,
                "raw_text": visible_text,
                "dream_text": dream_text
            }
            
        except Exception as e:
            logger.error(f"[SLMEngine] Vector Synthesis Error: {e}", exc_info=True)
            return {
                "vector": [0.0] * latent_dim,
                "raw_text": "",
                "dream_text": ""
            }

    def dream_scenario_vector(self, system_instruction: str, user_prompt: str) -> list:
        """
        Generates a creative scenario internally and returns ONLY its numerical vector.
        """
        result = self.dream_daily_scenario(system_instruction, user_prompt)
        return result.get("vector", [])


    def release(self) -> None:
        """
        Fully releases the LLM from memory to free resources for other models.
        After calling this, the engine cannot generate new vectors until reloaded.
        This is a heavier model (~4GB) — releasing it before CSDI/VAE-TCN
        is critical for machines with limited memory.
        """
        if hasattr(self, 'llm') and self.llm is not None:
            logger.info("[SLMEngine] Releasing LLM from memory...")
            del self.llm
            self.llm = None
            
            if hasattr(self, 'telemetry') and self.telemetry:
                self.telemetry.stop()
                
            gc.collect()
            logger.info("[SLMEngine] LLM released successfully. ~4GB freed.")
        else:
            logger.info("[SLMEngine] LLM already released, nothing to free.")

# Self-test block
if __name__ == "__main__":
    try:
        print("Testing Vector Generation with Enhanced Cognitive Context...")
        engine = SLMEngine()
        cfg_prompts = engine.config.get("prompts", {})
        sys_test = cfg_prompts.get("test_system_prompt", "You are an expert traffic scenario simulator.")
        user_test = cfg_prompts.get("test_user_prompt", "Imagine a chaotic stormy Monday morning.")
        vector = engine.dream_scenario_vector(sys_test, user_test)
        print(f"\nGenerated Vector Dimension: {len(vector)}")
        print(f"First 5 dimensions: {vector[:5]}...")
    except Exception as err:
        print(f"\nTest Failed: {err}")