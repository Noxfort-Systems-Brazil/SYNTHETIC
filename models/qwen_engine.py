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
# File: models/qwen_engine.py
# Author: Gabriel Moraes
# Date: 2026-02-26

import gc
import os
import re
import sys
import numpy as np

# Attempt to import the inference library
try:
    from llama_cpp import Llama
except ImportError:
    print("[CRITICAL] llama-cpp-python not installed. Please run: pip install llama-cpp-python")
    sys.exit(1)

class QwenEngine:
    """
    Wrapper class for the Qwen3 1.7B GGUF Model optimized for Vector output.
    It focuses on extracting semantic embeddings (Latent Vectors) rather than just text.
    """

    # Context window set to 8192 to allow deep cognitive reasoning (Thinking Mode)
    def __init__(self, model_path: str = None, n_ctx: int = 8192, n_gpu_layers: int = 0):
        """
        Initializes the inference engine with Embedding support enabled.
        """
        if model_path is None:
            # Automatic path resolution (lowercase 'vault')
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.model_path = os.path.join(base_dir, "models", "vault", "Qwen3-1.7B-Q8_0.gguf")
        else:
            self.model_path = model_path

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"[QwenEngine] Model file not found at: {self.model_path}\n"
                "Please run 'download_qwen.py' first or move the model to the correct directory."
            )

        print(f"[QwenEngine] Loading model for Vector Synthesis from: {self.model_path}...")
        print(f"[QwenEngine] Context Window Capacity: {n_ctx} tokens.")

        try:
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                verbose=False,
                embedding=True  # CRITICAL: Enables vector extraction
            )
            print("[QwenEngine] Vector Engine loaded successfully.")
        except Exception as e:
            raise RuntimeError(f"[QwenEngine] Failed to initialize Llama context: {e}")

    def dream_scenario_vector(self, system_instruction: str, user_prompt: str) -> list:
        """
        Generates a creative scenario internally (Transient Memory) and returns ONLY its 
        numerical vector representation (Embedding).
        
        The text is generated, encoded, and immediately discarded after being printed.
        
        Args:
            system_instruction (str): The persona/rules.
            user_prompt (str): The specific day context.

        Returns:
            list[float]: A high-dimensional vector representing the 'feeling' of the scenario.
        """
        
        # Injecting the Cognitive Directive to force Chain-of-Thought (Thinking Mode)
        cognitive_instruction = (
            system_instruction + 
            "\n\n[CRITICAL DIRECTIVE]: You are in THINKING MODE. "
            "Before providing the final scenario, you MUST open a <think> tag and write out your step-by-step "
            "logical reasoning about the weather, traffic density, and physical constraints of the requested situation. "
            "Close with </think> and then write the final scenario description."
        )

        # 1. Generate the creative text (The "Dream") in memory
        messages = [
            {"role": "system", "content": cognitive_instruction},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # High temperature for diverse "dreams", expanded max_tokens for deep thoughts
            completion = self.llm.create_chat_completion(
                messages=messages,
                temperature=0.85, 
                max_tokens=1024
            )
            dream_text = completion['choices'][0]['message']['content']
            
            # Strip <think>...</think> for display — thinking is internal only
            # The full text (with thinking) is still used for embedding generation
            visible_text = re.sub(r'<think>.*?</think>', '', dream_text, flags=re.DOTALL).strip()
            
            print("\n" + "="*50)
            print("[SYNAPSE COGNITIVE ENGINE] Scenario Description:")
            print("-" * 50)
            print(visible_text if visible_text else "[Thinking mode active — scenario encoded directly]")
            print("="*50 + "\n")
            
            # 2. Convert the Dream (Thoughts + Scenario) to a Vector (Embedding)
            print("[QwenEngine] Converting thoughts into Latent Vector...")
            embedding_response = self.llm.create_embedding(dream_text)
            
            # Extract the raw vector list
            raw_vector = embedding_response['data'][0]['embedding']
            
            # Qwen3 1.7B latent dimension target
            latent_dim = 2048
            
            # Robust Mean Pooling to handle variable llama.cpp output structures
            if isinstance(raw_vector[0], list):
                # Output is a list of token vectors: [[...], [...], ...]
                print(f"[QwenEngine] Nested token embeddings detected. Pooling {len(raw_vector)} tokens...")
                vector_matrix = np.array(raw_vector)
                vector = vector_matrix.mean(axis=0).tolist()
            else:
                # Output is a flat list
                if len(raw_vector) > latent_dim and len(raw_vector) % latent_dim == 0:
                    # Flattened token array
                    print(f"[QwenEngine] Flat token embeddings detected. Pooling...")
                    num_tokens = len(raw_vector) // latent_dim
                    vector_matrix = np.array(raw_vector).reshape(num_tokens, latent_dim)
                    vector = vector_matrix.mean(axis=0).tolist()
                else:
                    # Already a single vector (or needs truncation)
                    vector = raw_vector[:latent_dim]
            
            # Failsafe padding just to guarantee the exact shape for VAE-TCN
            if len(vector) < latent_dim:
                vector = vector + [0.0] * (latent_dim - len(vector))
            
            return vector
            
        except Exception as e:
            print(f"[QwenEngine] Vector Synthesis Error: {e}")
            # Return a zero-vector fallback for 1.7B models
            return [0.0] * 2048

    def release(self):
        """
        Fully releases the LLM from memory to free resources for other models.
        After calling this, the engine cannot generate new vectors until reloaded.
        This is the heaviest model (~1.7GB) — releasing it before CSDI/VAE-TCN
        is critical for machines with limited memory.
        """
        if hasattr(self, 'llm') and self.llm is not None:
            print("[QwenEngine] Releasing LLM from memory...")
            del self.llm
            self.llm = None
            gc.collect()
            print("[QwenEngine] LLM released successfully. ~1.7GB freed.")
        else:
            print("[QwenEngine] LLM already released, nothing to free.")

# Self-test block
if __name__ == "__main__":
    try:
        print("Testing Vector Generation with Enhanced Cognitive Context...")
        engine = QwenEngine()
        vector = engine.dream_scenario_vector(
            "You are an expert traffic scenario simulator.", 
            "Imagine a chaotic stormy Monday morning."
        )
        print(f"\nGenerated Vector Dimension: {len(vector)}")
        print(f"First 5 dimensions: {vector[:5]}...")
    except Exception as err:
        print(f"\nTest Failed: {err}")