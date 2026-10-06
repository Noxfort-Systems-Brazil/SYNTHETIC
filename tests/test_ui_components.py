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
# File: tests/test_ui_components.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import os
import unittest
from typing import Any, Callable, Dict, List, Optional

from src.core.map_provider import MapProvider
from ui.config_builder import SimulationConfigBuilder
from ui.dialog_service import IDialogService
from ui.interfaces import ITranslator
from ui.translator import Translator


class MockTranslator(ITranslator):
    """Mock translator for testing UI localization decoupling."""

    def __init__(self) -> None:
        self.locale = "en"

    def t(self, key: str, *args: Any) -> str:
        if args:
            return f"[{key}_{args[0]}]"
        return f"[{key}]"

    def set_locale(self, locale_code: str) -> None:
        self.locale = locale_code

    def get_locale(self) -> str:
        return self.locale

    def get_supported_locales(self) -> Dict[str, str]:
        return {"MockEnglish": "en", "MockFrench": "fr"}


class MockDialogService(IDialogService):
    """Mock dialog service for isolated headless UI testing."""

    def __init__(self) -> None:
        self.last_error: Optional[str] = None
        self.last_info: Optional[str] = None
        self.directory_to_return: Optional[str] = "/mock/dir"
        self.map_file_to_return: Optional[str] = "/mock/map.osm"
        self.opened_map_selector: bool = False

    def show_error(self, title: str, message: str) -> None:
        self.last_error = f"{title}: {message}"

    def show_info(self, title: str, message: str) -> None:
        self.last_info = f"{title}: {message}"

    def ask_directory(self, initial_dir: str) -> Optional[str]:
        return self.directory_to_return

    def ask_map_file(self, title: str) -> Optional[str]:
        return self.map_file_to_return

    def open_map_selector(
        self,
        parent: Any,
        map_provider: MapProvider,
        num_cameras: int,
        num_loops: int,
        on_complete: Callable[[Optional[List[Dict[str, float]]], Optional[List[Dict[str, float]]]], None],
    ) -> None:
        self.opened_map_selector = True


class TestUIComponents(unittest.TestCase):
    def test_simulation_config_builder(self):
        provider = MapProvider()
        provider.bounds = (-23.5, -51.2, -23.4, -51.1)

        sources = {"waze": True, "tomtom": False, "loop": True, "camera": False}
        problems = {"gaps": True, "anomalies": False}
        cameras = [{"lat": -23.45, "lon": -51.15}]
        loops = [{"lat": -23.46, "lon": -51.16}]

        config = SimulationConfigBuilder.build(
            sources=sources,
            problems=problems,
            duration_days=2,
            interval_seconds=15,
            flow_level="Grande",
            slm_mode="Ultrarealista",
            num_cameras=1,
            num_loops=1,
            base_output_dir="/tmp/test_synthetic",
            folder_name="scenario_01",
            map_provider=provider,
            cameras=cameras,
            loops=loops,
        )

        self.assertIn("sources", config)
        self.assertTrue(config["sources"]["waze"])
        self.assertFalse(config["sources"]["tomtom"])

        self.assertIn("simulation", config)
        self.assertEqual(config["simulation"]["duration_days"], 2)
        self.assertEqual(config["simulation"]["flow_level"], "Grande")

        self.assertIn("map", config)
        self.assertEqual(config["map"]["bounds"], (-23.5, -51.2, -23.4, -51.1))
        self.assertEqual(len(config["map"]["local_points"]["cameras"]), 1)
        self.assertEqual(len(config["map"]["local_points"]["loops"]), 1)

        self.assertEqual(
            config["output_directory"], os.path.join("/tmp/test_synthetic", "scenario_01")
        )

    def test_mock_dialog_service(self):
        mock_dialog = MockDialogService()
        mock_dialog.show_error("Error", "Missing file")
        self.assertEqual(mock_dialog.last_error, "Error: Missing file")

        mock_dialog.show_info("Success", "Done")
        self.assertEqual(mock_dialog.last_info, "Success: Done")

        chosen_dir = mock_dialog.ask_directory("/initial")
        self.assertEqual(chosen_dir, "/mock/dir")

    def test_translator_service(self):
        translator = Translator()
        locales = translator.get_supported_locales()
        self.assertIn("English", locales)
        self.assertIn("Português (Brasil)", locales)
        self.assertEqual(locales["English"], "en")

        mock_tr = MockTranslator()
        self.assertEqual(mock_tr.t("app_title"), "[app_title]")
        self.assertEqual(mock_tr.t("msg", "param"), "[msg_param]")
        mock_tr.set_locale("fr")
        self.assertEqual(mock_tr.get_locale(), "fr")


if __name__ == "__main__":
    unittest.main()
