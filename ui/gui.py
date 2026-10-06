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
# File: ui/gui.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import os
import tkinter as tk
from typing import Any, Callable, Dict, List, Optional

from src.core.logger import logger
from src.core.map_provider import MapProvider, OSMMapProvider
from ui.config_builder import SimulationConfigBuilder
from ui.dialog_service import IDialogService, TkDialogService
from ui.main_view import MainView
from ui.translator import translator


class DataGeneratorApp(tk.Tk):
    """
    Main Application Window acting as a pure Facade and Orchestrator.
    Decouples visual widget rendering (MainView), modal dialogs (TkDialogService),
    and simulation configuration compilation (SimulationConfigBuilder).
    """

    def __init__(
        self,
        on_generate_callback: Optional[
            Callable[[Dict[str, Any], Callable[[str], None], Callable[[Exception], None]], None]
        ] = None,
        dialog_service: Optional[IDialogService] = None,
        config_builder: Optional[SimulationConfigBuilder] = None,
    ) -> None:
        super().__init__()

        self.on_generate_callback = on_generate_callback
        self.dialog_service: IDialogService = dialog_service if dialog_service is not None else TkDialogService()
        self.config_builder: SimulationConfigBuilder = (
            config_builder if config_builder is not None else SimulationConfigBuilder()
        )

        # Initialize and mount visual view
        self.view = MainView(
            parent=self,
            on_select_output_dir=self.select_output_dir,
            on_select_map_file=self.select_osm_file,
            on_start_generation=self.start_generation,
        )

    # --- Backwards compatibility variable properties forwarding to view ---
    @property
    def var_waze(self) -> tk.BooleanVar:
        return self.view.var_waze

    @property
    def var_tomtom(self) -> tk.BooleanVar:
        return self.view.var_tomtom

    @property
    def var_loop(self) -> tk.BooleanVar:
        return self.view.var_loop

    @property
    def var_camera(self) -> tk.BooleanVar:
        return self.view.var_camera

    @property
    def var_gaps(self) -> tk.BooleanVar:
        return self.view.var_gaps

    @property
    def var_anomalies(self) -> tk.BooleanVar:
        return self.view.var_anomalies

    @property
    def var_duration(self) -> tk.IntVar:
        return self.view.var_duration

    @property
    def var_interval(self) -> tk.IntVar:
        return self.view.var_interval

    @property
    def var_flow_level(self) -> tk.StringVar:
        return self.view.var_flow_level

    @property
    def var_slm_mode(self) -> tk.StringVar:
        return self.view.var_slm_mode

    @property
    def var_num_cameras(self) -> tk.IntVar:
        return self.view.var_num_cameras

    @property
    def var_num_loops(self) -> tk.IntVar:
        return self.view.var_num_loops

    @property
    def var_output_dir(self) -> tk.StringVar:
        return self.view.var_output_dir

    @property
    def var_output_name(self) -> tk.StringVar:
        return self.view.var_output_name

    @property
    def var_osm_path(self) -> tk.StringVar:
        return self.view.var_osm_path

    @property
    def action_button(self) -> Any:
        return self.view.action_button

    def update_ui_texts(self) -> None:
        """Delegates localization update to view."""
        self.view.update_ui_texts()

    def select_output_dir(self) -> None:
        """Prompts user for output directory and updates state."""
        directory = self.dialog_service.ask_directory(self.view.var_output_dir.get())
        if directory:
            self.view.var_output_dir.set(directory)

    def select_osm_file(self) -> None:
        """Prompts user for map file and updates state."""
        filepath = self.dialog_service.ask_map_file(translator.t("section_map"))
        if filepath:
            self.view.var_osm_path.set(filepath)

    def start_generation(self) -> None:
        """Validates map file presence, loads map provider, and launches map selector."""
        osm_path = self.view.var_osm_path.get()
        if not osm_path or not os.path.exists(osm_path):
            self.dialog_service.show_error(translator.t("err_title"), translator.t("err_osm_missing"))
            return

        self.view.set_action_state("disabled", "btn_loading_map")

        try:
            map_provider: MapProvider = MapProvider.load_from_file(osm_path)
        except ValueError as e:
            self.dialog_service.show_error(translator.t("err_title"), translator.t("err_osm_failed", str(e)))
            self.view.set_action_state("normal", "btn_generate")
            return

        self.dialog_service.open_map_selector(
            parent=self,
            map_provider=map_provider,
            num_cameras=self.view.var_num_cameras.get(),
            num_loops=self.view.var_num_loops.get(),
            on_complete=lambda cams, loops: self._continue_generation_after_map(cams, loops, map_provider),
        )

    def _continue_generation_after_map(
        self,
        cameras: Optional[List[Dict[str, float]]],
        loops: Optional[List[Dict[str, float]]],
        map_provider: MapProvider,
    ) -> None:
        """Callback receiving sensor positions and launching simulation generation."""
        if cameras is None or loops is None:
            self.view.set_action_state("normal", "btn_generate")
            return

        self.view.set_action_state("disabled", "btn_generating")

        sources = {
            "waze": self.view.var_waze.get(),
            "tomtom": self.view.var_tomtom.get(),
            "loop": self.view.var_loop.get(),
            "camera": self.view.var_camera.get(),
        }
        problems = {
            "gaps": self.view.var_gaps.get(),
            "anomalies": self.view.var_anomalies.get(),
        }

        config = self.config_builder.build(
            sources=sources,
            problems=problems,
            duration_days=self.view.var_duration.get(),
            interval_seconds=self.view.var_interval.get(),
            flow_level=self.view.var_flow_level.get(),
            slm_mode=self.view.var_slm_mode.get(),
            num_cameras=self.view.var_num_cameras.get(),
            num_loops=self.view.var_num_loops.get(),
            base_output_dir=self.view.var_output_dir.get(),
            folder_name=self.view.var_output_name.get(),
            map_provider=map_provider,
            cameras=cameras,
            loops=loops,
        )

        if self.on_generate_callback:
            self.on_generate_callback(config, self.handle_success, self.handle_error)
        else:
            self.handle_error(ValueError("No generation callback provided!"))

    def handle_success(self, final_output_dir: str) -> None:
        """Thread-safe success handler dispatching to main thread."""
        self.after(0, self._on_generation_complete, final_output_dir)

    def handle_error(self, error: Exception) -> None:
        """Thread-safe error handler dispatching to main thread."""
        self.after(0, self._on_generation_error, error)

    def _on_generation_complete(self, final_output_dir: str) -> None:
        self.dialog_service.show_info(
            translator.t("success_title"), translator.t("success_msg", final_output_dir)
        )
        self.view.set_action_state("normal", "btn_generate")

    def _on_generation_error(self, error: Exception) -> None:
        logger.error(f"Simulation error: {str(error)}")
        self.dialog_service.show_error(
            translator.t("err_title"), translator.t("err_generation", str(error))
        )
        self.view.set_action_state("normal", "btn_generate")
