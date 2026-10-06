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
# File: tests/test_ui_views.py
# Author: Gabriel Moraes
# Date: 2026-09-29

import os
import tempfile
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import MagicMock

from src.core.map_provider import MapProvider
from tests.test_ui_components import MockDialogService, MockTranslator
from ui.components import (
    ActionSection,
    LanguageSection,
    MapSection,
    OutputSection,
    ProblemsSection,
    SettingsSection,
    SourcesSection,
)
from ui.gui import DataGeneratorApp
from ui.main_view import MainView
from ui.map_selector import MapSelectorWindow
from ui.translator import translator


class TestUIViews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def setUp(self):
        self.frame = ttk.Frame(self.root)
        self.frame.pack()
        self.mock_tr = MockTranslator()

    def tearDown(self):
        try:
            self.frame.destroy()
        except Exception:
            pass

    # ---------------------------------------------------------
    # 1. Component Sections Tests
    # ---------------------------------------------------------
    def test_settings_section(self):
        sec = SettingsSection(self.frame)
        settings = sec.get_settings()
        self.assertEqual(settings["duration_days"], 1)
        self.assertEqual(settings["interval_seconds"], 10)
        self.assertEqual(settings["flow_level"], "Médio")
        self.assertEqual(settings["slm_mode"], "Realista")
        self.assertEqual(settings["num_cameras"], 5)
        self.assertEqual(settings["num_loops"], 5)

        # Modify values
        sec.var_duration.set(3)
        sec.var_interval.set(30)
        sec.var_flow_level.set("Grande")
        sec.var_slm_mode.set("Ultrarealista")
        sec.var_num_cameras.set(8)
        sec.var_num_loops.set(12)

        updated = sec.get_settings()
        self.assertEqual(updated["duration_days"], 3)
        self.assertEqual(updated["interval_seconds"], 30)
        self.assertEqual(updated["flow_level"], "Grande")
        self.assertEqual(updated["slm_mode"], "Ultrarealista")
        self.assertEqual(updated["num_cameras"], 8)
        self.assertEqual(updated["num_loops"], 12)

        sec.update_ui_texts(self.mock_tr)
        self.assertEqual(sec.cget("text"), "[section_settings]")

    def test_sources_section(self):
        sec = SourcesSection(self.frame)
        sources = sec.get_sources()
        self.assertTrue(sources["waze"])
        self.assertTrue(sources["tomtom"])
        self.assertTrue(sources["loop"])
        self.assertTrue(sources["camera"])

        sec.var_waze.set(False)
        sec.var_tomtom.set(False)
        updated = sec.get_sources()
        self.assertFalse(updated["waze"])
        self.assertFalse(updated["tomtom"])

        sec.update_ui_texts(self.mock_tr)
        self.assertEqual(sec.cget("text"), "[section_sources]")

    def test_problems_section(self):
        sec = ProblemsSection(self.frame)
        problems = sec.get_problems()
        self.assertTrue(problems["gaps"])
        self.assertTrue(problems["anomalies"])

        sec.var_gaps.set(False)
        sec.var_anomalies.set(False)
        updated = sec.get_problems()
        self.assertFalse(updated["gaps"])
        self.assertFalse(updated["anomalies"])

        sec.update_ui_texts(self.mock_tr)
        self.assertEqual(sec.cget("text"), "[section_problems]")

    def test_output_section(self):
        mock_cb = MagicMock()
        sec = OutputSection(self.frame, on_select_output_dir=mock_cb)

        self.assertEqual(sec.var_output_name.get(), "output")
        sec.var_output_dir.set("/custom/output")
        sec.var_output_name.set("test_run")

        self.assertEqual(sec.var_output_dir.get(), "/custom/output")
        self.assertEqual(sec.var_output_name.get(), "test_run")

        sec.update_ui_texts(self.mock_tr)
        self.assertEqual(sec.cget("text"), "[section_output]")

    def test_map_section(self):
        on_select_map = MagicMock()
        sec = MapSection(self.frame, on_select_map_file=on_select_map)

        sec.var_osm_path.set("/path/to/city.osm")
        self.assertEqual(sec.var_osm_path.get(), "/path/to/city.osm")

        sec.update_ui_texts(self.mock_tr)
        self.assertEqual(sec.cget("text"), "[section_map]")

    def test_language_section(self):
        on_lang_change = MagicMock()
        sec = LanguageSection(self.frame, translator=self.mock_tr, on_locale_changed=on_lang_change)

        mock_event = MagicMock()
        sec.combo_lang.set("MockFrench")
        sec._on_combo_select(mock_event)
        on_lang_change.assert_called_once_with("fr")

        sec.update_ui_texts(self.mock_tr)
        self.assertEqual(sec.lbl_lang.cget("text"), "[lang_label]")

    def test_action_section(self):
        on_start = MagicMock()
        sec = ActionSection(self.frame, on_start_generation=on_start)

        sec.set_action_state("disabled", "btn_generating", self.mock_tr)
        self.assertEqual(str(sec.action_button.cget("state")), "disabled")

        sec.set_action_state("normal", "btn_generate", self.mock_tr)
        self.assertEqual(str(sec.action_button.cget("state")), "normal")

        sec.update_ui_texts(self.mock_tr)
        self.assertEqual(sec.action_button.cget("text"), "[btn_generate]")

    # ---------------------------------------------------------
    # 2. MainView Composite Tests
    # ---------------------------------------------------------
    def test_main_view_integration(self):
        view = MainView(
            parent=self.root,
            on_select_output_dir=MagicMock(),
            on_select_map_file=MagicMock(),
            on_start_generation=MagicMock(),
            translator=self.mock_tr,
        )

        # Verify property forwarders
        self.assertEqual(view.var_duration.get(), 1)
        self.assertEqual(view.var_flow_level.get(), "Médio")
        self.assertTrue(view.var_waze.get())
        self.assertTrue(view.var_gaps.get())

        # Verify update_ui_texts
        view.update_ui_texts()
        self.assertEqual(view.settings_section.cget("text"), "[section_settings]")
        self.assertEqual(view.sources_section.cget("text"), "[section_sources]")

        # Test set_action_state
        view.set_action_state("disabled", "btn_generating")
        self.assertEqual(str(view.action_button.cget("state")), "disabled")
        view.destroy()

    # ---------------------------------------------------------
    # 3. MapSelectorWindow Tests
    # ---------------------------------------------------------
    def test_map_selector_window_lifecycle(self):
        mock_provider = MagicMock(spec=MapProvider)
        mock_provider.get_bounds.return_value = (-23.55, -51.25, -23.45, -51.15)
        mock_provider.snap_to_road.side_effect = lambda lat, lon: (lat + 0.001, lon + 0.001)

        completed_data = {}

        def on_complete(cameras, loops):
            completed_data["cameras"] = cameras
            completed_data["loops"] = loops

        selector = MapSelectorWindow(
            parent=self.root,
            map_provider=mock_provider,
            num_cameras=1,
            num_loops=1,
            on_complete_callback=on_complete,
        )

        self.assertEqual(selector.state, 0)

        # Place camera
        selector.add_marker((-23.50, -51.20))
        self.assertEqual(len(selector.selected_cameras), 1)
        self.assertEqual(selector.state, 1)

        # Place loop
        selector.add_marker((-23.51, -51.21))
        self.assertEqual(len(selector.selected_loops), 1)
        self.assertEqual(selector.state, 2)

        # Confirm and close
        selector.confirm_and_close()
        self.assertEqual(len(completed_data["cameras"]), 1)
        self.assertEqual(len(completed_data["loops"]), 1)

    def test_map_selector_window_cancelled(self):
        mock_provider = MagicMock(spec=MapProvider)
        mock_provider.get_bounds.return_value = None

        cancelled_data = {}

        def on_complete(cameras, loops):
            cancelled_data["cameras"] = cameras
            cancelled_data["loops"] = loops

        selector = MapSelectorWindow(
            parent=self.root,
            map_provider=mock_provider,
            num_cameras=1,
            num_loops=0,
            on_complete_callback=on_complete,
        )

        selector.on_close()
        self.assertIsNone(cancelled_data["cameras"])
        self.assertIsNone(cancelled_data["loops"])

    # ---------------------------------------------------------
    # 4. DataGeneratorApp Facade Tests
    # ---------------------------------------------------------
    def test_data_generator_app_flows(self):
        mock_callback = MagicMock()
        mock_dialog = MockDialogService()

        app = DataGeneratorApp(
            on_generate_callback=mock_callback,
            dialog_service=mock_dialog,
        )
        app.withdraw()

        # 1. Select output directory
        mock_dialog.directory_to_return = "/test/chosen_output"
        app.select_output_dir()
        self.assertEqual(app.view.var_output_dir.get(), "/test/chosen_output")

        # 2. Select OSM file
        mock_dialog.map_file_to_return = "/test/chosen_map.osm"
        app.select_osm_file()
        self.assertEqual(app.view.var_osm_path.get(), "/test/chosen_map.osm")

        # 3. Start generation when map file does NOT exist
        app.view.var_osm_path.set("/non/existent/map.osm")
        app.start_generation()
        self.assertIn(translator.t("err_osm_missing"), mock_dialog.last_error)

        # 4. Start generation with valid map file
        with tempfile.NamedTemporaryFile("w", suffix=".osm", delete=False) as f:
            f.write("<osm><bounds minlat='-23.5' minlon='-51.2' maxlat='-23.4' maxlon='-51.1'/></osm>")
            valid_osm = f.name

        try:
            app.view.var_osm_path.set(valid_osm)
            app.start_generation()
            self.assertTrue(mock_dialog.opened_map_selector)

            # Test continuation after map selection (with None - cancelled)
            app._continue_generation_after_map(None, None, MagicMock())
            mock_callback.assert_not_called()

            # Test continuation after map selection (with valid points)
            cams = [{"lat": -23.45, "lon": -51.15}]
            loops = [{"lat": -23.46, "lon": -51.16}]
            mock_map_provider = MagicMock(spec=MapProvider)
            mock_map_provider.bounds = (-23.5, -51.2, -23.4, -51.1)

            app._continue_generation_after_map(cams, loops, mock_map_provider)
            mock_callback.assert_called_once()

            # Test handle_success
            app._on_generation_complete("/final/output/dir")
            self.assertIn("/final/output/dir", mock_dialog.last_info)

            # Test handle_error
            app._on_generation_error(RuntimeError("Test error"))
            self.assertIn("Test error", mock_dialog.last_error)

        finally:
            if os.path.exists(valid_osm):
                os.remove(valid_osm)
            app.destroy()


if __name__ == "__main__":
    unittest.main()
