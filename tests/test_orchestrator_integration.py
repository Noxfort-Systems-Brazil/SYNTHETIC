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
# File: tests/test_orchestrator_integration.py
# Author: Gabriel Moraes
# Date: 2026-09-29

import datetime
import unittest
from unittest.mock import MagicMock, patch
import torch

from src.core.flow_schedule import FlowScheduleValidator
from src.core.map_provider import MapProvider
from src.core.simulation_logic import SimulationOrchestrator
from src.core.traffic_simulator import (
    SmallFlowStrategy,
    MediumFlowStrategy,
    LargeFlowStrategy,
    ChaoticFlowStrategy,
)
import main


class TestSimulationOrchestrator(unittest.TestCase):
    def setUp(self):
        self.config = {
            "simulation": {
                "duration_days": 1,
                "interval_seconds": 3600,  # 1 hour steps = 24 steps
                "flow_level": "Médio",
                "slm_mode": "Realista"
            },
            "problems": {
                "gaps": True,
                "anomalies": True
            },
            "sources": {
                "tomtom": True,
                "waze": True,
                "camera": False,
                "loop": False
            },
            "output_directory": "/tmp/synthetic_test_output",
            "map": {}
        }
        self.mock_generator = MagicMock()

    @patch("src.core.simulation_logic.SLMEngine")
    @patch("src.core.simulation_logic.ScreenwriterAgent")
    @patch("src.core.simulation_logic.DirectorAgent")
    def test_orchestrator_init_flow_strategies(self, mock_director_cls, mock_screenwriter_cls, mock_slm_cls):
        # Medium
        orch_med = SimulationOrchestrator(self.config, [self.mock_generator])
        self.assertIsInstance(orch_med.traffic_simulator.strategy, MediumFlowStrategy)

        # Small
        cfg_small = dict(self.config)
        cfg_small["simulation"] = dict(self.config["simulation"], flow_level="Pequeno")
        orch_small = SimulationOrchestrator(cfg_small, [self.mock_generator])
        self.assertIsInstance(orch_small.traffic_simulator.strategy, SmallFlowStrategy)

        # Large
        cfg_large = dict(self.config)
        cfg_large["simulation"] = dict(self.config["simulation"], flow_level="Grande")
        orch_large = SimulationOrchestrator(cfg_large, [self.mock_generator])
        self.assertIsInstance(orch_large.traffic_simulator.strategy, LargeFlowStrategy)

        # Chaotic
        cfg_chaotic = dict(self.config)
        cfg_chaotic["simulation"] = dict(self.config["simulation"], flow_level="Caótico")
        orch_chaotic = SimulationOrchestrator(cfg_chaotic, [self.mock_generator])
        self.assertIsInstance(orch_chaotic.traffic_simulator.strategy, ChaoticFlowStrategy)

    @patch("src.core.simulation_logic.LightweightGATv2")
    @patch("src.core.simulation_logic.SLMEngine")
    @patch("src.core.simulation_logic.ScreenwriterAgent")
    @patch("src.core.simulation_logic.DirectorAgent")
    def test_orchestrator_map_topology_extraction(self, mock_dir, mock_screen, mock_slm, mock_gat_cls):
        mock_gat = MagicMock()
        mock_gat.extract_context.return_value = torch.ones((1, 32))
        mock_gat_cls.return_value = mock_gat

        cfg_with_map = dict(self.config)
        mock_map = MagicMock(spec=MapProvider)
        cfg_with_map["map"] = {"provider": mock_map}

        orch = SimulationOrchestrator(cfg_with_map, [self.mock_generator])
        self.assertIsNotNone(orch.graph_embedding)
        mock_gat.extract_context.assert_called_once_with(mock_map)

    @patch("src.core.simulation_logic.SLMEngine")
    @patch("src.core.simulation_logic.ScreenwriterAgent")
    @patch("src.core.simulation_logic.DirectorAgent")
    def test_orchestrator_run_successful_lifecycle(self, mock_director_cls, mock_screenwriter_cls, mock_slm_cls):
        mock_slm = MagicMock()
        mock_slm_cls.return_value = mock_slm

        mock_screenwriter = MagicMock()
        mock_screenwriter_cls.return_value = mock_screenwriter

        schedule = FlowScheduleValidator.create_default_schedule(peak_level=2)
        mock_screenwriter.create_daily_script.return_value = {
            "date": "2026-10-05",
            "scenario_vector": [0.1] * 2048,
            "flow_schedule": schedule,
            "metadata": {"day_of_week": "Monday"}
        }

        mock_director = MagicMock()
        mock_director_cls.return_value = mock_director
        # 24 steps in 1 day with 3600 interval
        mock_director.action.return_value = {
            "vehicle_flow": [50.0] * 24,
            "current_speed": [60.0] * 24
        }

        orch = SimulationOrchestrator(self.config, [self.mock_generator])
        success, error = orch.run()

        self.assertTrue(success)
        self.assertIsNone(error)

        # Verify Phase 1: SLM released
        mock_slm.release.assert_called_once()

        # Verify Phase 2: Director action called and generators generated data
        mock_director.action.assert_called_once()
        self.assertGreater(self.mock_generator.generate.call_count, 0)

    @patch("src.core.simulation_logic.SLMEngine")
    @patch("src.core.simulation_logic.ScreenwriterAgent")
    @patch("src.core.simulation_logic.DirectorAgent")
    def test_orchestrator_run_handles_runtime_error(self, mock_dir_cls, mock_screen_cls, mock_slm_cls):
        mock_screenwriter = MagicMock()
        mock_screen_cls.return_value = mock_screenwriter
        mock_screenwriter.create_daily_script.side_effect = RuntimeError("Screenwriter failed")

        orch = SimulationOrchestrator(self.config, [self.mock_generator])
        success, error = orch.run()

        self.assertFalse(success)
        self.assertIsInstance(error, RuntimeError)


class TestMainExecutionPipeline(unittest.TestCase):
    def setUp(self):
        self.config = {
            "sources": {
                "tomtom": True,
                "waze": False,
                "camera": False,
                "loop": False
            },
            "simulation": {
                "duration_days": 1,
                "interval_seconds": 60,
                "flow_level": "Médio"
            },
            "problems": {"gaps": False, "anomalies": False},
            "output_directory": "/tmp/main_pipeline_test"
        }

    @patch("src.globalf.tomtom_generator.TomTomGenerator")
    @patch("src.core.simulation_logic.SimulationOrchestrator")
    def test_run_simulation_success(self, mock_orchestrator_cls, mock_tomtom_cls):
        mock_orch = MagicMock()
        mock_orch.run.return_value = (True, None)
        mock_orchestrator_cls.return_value = mock_orch

        on_success = MagicMock()
        on_error = MagicMock()

        main.run_simulation(self.config, on_success, on_error)

        on_success.assert_called_once_with("/tmp/main_pipeline_test")
        on_error.assert_not_called()

    @patch("src.globalf.tomtom_generator.TomTomGenerator")
    @patch("src.core.simulation_logic.SimulationOrchestrator")
    def test_run_simulation_failure_callback(self, mock_orchestrator_cls, mock_tomtom_cls):
        mock_orch = MagicMock()
        test_err = RuntimeError("Orchestration crashed")
        mock_orch.run.return_value = (False, test_err)
        mock_orchestrator_cls.return_value = mock_orch

        on_success = MagicMock()
        on_error = MagicMock()

        main.run_simulation(self.config, on_success, on_error)

        on_success.assert_not_called()
        on_error.assert_called_once_with(test_err)

    @patch("main.run_simulation")
    def test_start_simulation_spawns_thread(self, mock_run_sim):
        on_success = MagicMock()
        on_error = MagicMock()

        main.start_simulation(self.config, on_success, on_error)

        # Allow thread to execute
        import time
        time.sleep(0.1)

        mock_run_sim.assert_called_once_with(self.config, on_success, on_error)


if __name__ == "__main__":
    unittest.main()
