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
# File: tests/test_screenwriter_and_slm.py
# Author: Gabriel Moraes
# Date: 2026-09-29

import datetime
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.agents.screenwriter import ScreenwriterAgent
from src.models.slm_engine import SLMEngine


class TestScreenwriterAgent(unittest.TestCase):
    def setUp(self):
        self.mock_llm = MagicMock()
        self.agent = ScreenwriterAgent(llm_engine=self.mock_llm)

    def test_config_loading_failure_modes(self):
        # Inexistent file
        agent_bad = ScreenwriterAgent(self.mock_llm, config_path="/non/existent/path.json")
        self.assertEqual(agent_bad.config, {})

        # Corrupt JSON file
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("{invalid_json:")
            bad_json_path = f.name
        try:
            agent_corrupt = ScreenwriterAgent(self.mock_llm, config_path=bad_json_path)
            self.assertEqual(agent_corrupt.config, {})
        finally:
            if os.path.exists(bad_json_path):
                os.remove(bad_json_path)

    def test_create_daily_script_with_dream_daily_scenario(self):
        self.mock_llm.dream_daily_scenario.return_value = {
            "vector": [0.1] * 2048,
            "raw_text": "SLOT 15: HIGH\nSLOT 36: PEAK",
            "dream_text": "<think>traffic reasoning</think>SLOT 15: HIGH\nSLOT 36: PEAK"
        }

        test_date = datetime.date(2026, 10, 5)  # Monday
        constraints = {
            "flow_level": "grande",
            "weather": "Rain",
            "previous_weather": "Sunny",
            "next_weather_forecast": "Overcast",
            "start_time": "08:00:00"
        }

        script = self.agent.create_daily_script(test_date, constraints)

        self.assertEqual(script["date"], "2026-10-05")
        self.assertEqual(script["metadata"]["flow_level"], "grande")
        self.assertEqual(script["metadata"]["city_size"], "Metropolis")
        self.assertEqual(script["metadata"]["weather"], "Rain")
        self.assertEqual(len(script["scenario_vector"]), 2048)
        self.assertIsNotNone(script["flow_schedule"])

    def test_create_daily_script_persisting_weather(self):
        self.mock_llm.dream_daily_scenario.return_value = {
            "vector": [0.5] * 2048,
            "raw_text": "Normal day",
            "dream_text": "Normal day"
        }

        test_date = datetime.date(2026, 10, 6)
        constraints = {
            "flow_level": "caótico",
            "weather": "Thunderstorm",
            "previous_weather": "Thunderstorm",
        }

        script = self.agent.create_daily_script(test_date, constraints)
        self.assertEqual(script["metadata"]["city_size"], "Megalopolis")
        self.assertEqual(script["metadata"]["weather"], "Thunderstorm")

    def test_create_daily_script_fallback_to_dream_scenario_vector(self):
        mock_simple_llm = MagicMock(spec=["dream_scenario_vector"])
        mock_simple_llm.dream_scenario_vector.return_value = [0.2] * 2048

        agent = ScreenwriterAgent(llm_engine=mock_simple_llm)
        test_date = datetime.date(2026, 10, 7)
        script = agent.create_daily_script(test_date, {"flow_level": "pequeno"})

        self.assertEqual(script["metadata"]["city_size"], "Small City")
        self.assertEqual(len(script["scenario_vector"]), 2048)
        self.assertIsNotNone(script["flow_schedule"])


class TestSLMEngine(unittest.TestCase):
    def test_model_not_found_raises_file_not_found_error(self):
        with self.assertRaises(FileNotFoundError):
            SLMEngine(model_path="/path/that/does/not/exist/model.gguf")

    @patch("src.models.slm_engine.Llama")
    @patch("src.models.slm_engine.HardwareTelemetry")
    def test_dream_daily_scenario_with_mocked_llama(self, mock_telemetry_cls, mock_llama_cls):
        mock_llama = MagicMock()
        mock_llama_cls.return_value = mock_llama

        # Create dummy existing file for model_path
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("dummy model weights")
            model_dummy_path = f.name

        try:
            mock_llama.create_chat_completion.return_value = {
                "choices": [{
                    "message": {
                        "content": "<think>Complex traffic reasoning...</think>Dense congested morning on the avenue."
                    }
                }]
            }
            # Mock flat embedding
            mock_llama.create_embedding.return_value = {
                "data": [{
                    "embedding": [0.05] * 2048
                }]
            }

            engine = SLMEngine(model_path=model_dummy_path)
            res = engine.dream_daily_scenario("SysPrompt", "UserPrompt")

            self.assertEqual(res["raw_text"], "Dense congested morning on the avenue.")
            self.assertIn("<think>", res["dream_text"])
            self.assertEqual(len(res["vector"]), 2048)
            self.assertEqual(res["vector"][0], 0.05)

            # Test dream_scenario_vector
            vec = engine.dream_scenario_vector("Sys", "User")
            self.assertEqual(len(vec), 2048)

            # Test release
            engine.release()
            self.assertIsNone(engine.llm)
            # Second release is idempotent
            engine.release()

        finally:
            if os.path.exists(model_dummy_path):
                os.remove(model_dummy_path)

    @patch("src.models.slm_engine.Llama")
    @patch("src.models.slm_engine.HardwareTelemetry")
    def test_dream_daily_scenario_nested_embeddings_pooling(self, mock_telemetry_cls, mock_llama_cls):
        mock_llama = MagicMock()
        mock_llama_cls.return_value = mock_llama

        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("dummy")
            model_dummy_path = f.name

        try:
            # Only thinking tag without visible text
            mock_llama.create_chat_completion.return_value = {
                "choices": [{
                    "message": {
                        "content": "<think>Internal thoughts only</think>"
                    }
                }]
            }
            # Nested tokens: 3 tokens, each length 2048
            token_1 = [1.0] * 2048
            token_2 = [2.0] * 2048
            token_3 = [3.0] * 2048
            mock_llama.create_embedding.return_value = {
                "data": [{
                    "embedding": [token_1, token_2, token_3]
                }]
            }

            engine = SLMEngine(model_path=model_dummy_path)
            res = engine.dream_daily_scenario("Sys", "User")

            self.assertEqual(res["raw_text"], "")
            self.assertEqual(len(res["vector"]), 2048)
            # Average of 1.0, 2.0, 3.0 is 2.0
            self.assertAlmostEqual(res["vector"][0], 2.0, places=4)
        finally:
            if os.path.exists(model_dummy_path):
                os.remove(model_dummy_path)

    @patch("src.models.slm_engine.Llama")
    @patch("src.models.slm_engine.HardwareTelemetry")
    def test_dream_daily_scenario_exception_fallback(self, mock_telemetry_cls, mock_llama_cls):
        mock_llama = MagicMock()
        mock_llama_cls.return_value = mock_llama
        mock_llama.create_chat_completion.side_effect = RuntimeError("Inference timeout")

        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("dummy")
            model_dummy_path = f.name

        try:
            engine = SLMEngine(model_path=model_dummy_path)
            res = engine.dream_daily_scenario("Sys", "User")
            self.assertEqual(len(res["vector"]), 2048)
            self.assertEqual(res["vector"], [0.0] * 2048)
            self.assertEqual(res["raw_text"], "")
        finally:
            if os.path.exists(model_dummy_path):
                os.remove(model_dummy_path)


if __name__ == "__main__":
    unittest.main()
