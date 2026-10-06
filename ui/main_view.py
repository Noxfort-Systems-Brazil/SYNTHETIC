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
# File: ui/main_view.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional

from ui.components import (
    ActionSection,
    LanguageSection,
    MapSection,
    OutputSection,
    ProblemsSection,
    SettingsSection,
    SourcesSection,
)
from ui.interfaces import ITranslator
from ui.translator import translator as global_translator


class MainView(ttk.Frame):
    """
    Composite View and Facade for the main visual dashboard.
    Coordinates child visual sections and dynamically binds localization events.
    """

    def __init__(
        self,
        parent: tk.Tk,
        on_select_output_dir: Callable[[], None],
        on_select_map_file: Callable[[], None],
        on_start_generation: Callable[[], None],
        translator: Optional[ITranslator] = None,
    ) -> None:
        super().__init__(parent, padding="10")
        self.pack(fill="both", expand=True)

        self.translator: ITranslator = translator if translator is not None else global_translator
        self.on_select_output_dir = on_select_output_dir
        self.on_select_map_file = on_select_map_file
        self.on_start_generation = on_start_generation

        # Mount modular visual sections
        self.language_section = LanguageSection(
            parent=self,
            translator=self.translator,
            on_locale_changed=self.on_language_change,
        )
        self.sources_section = SourcesSection(parent=self)
        self.problems_section = ProblemsSection(parent=self)
        self.settings_section = SettingsSection(parent=self)
        self.output_section = OutputSection(parent=self, on_select_output_dir=self.on_select_output_dir)
        self.map_section = MapSection(parent=self, on_select_map_file=self.on_select_map_file)
        self.action_section = ActionSection(parent=self, on_start_generation=self.on_start_generation)

        self.update_ui_texts()

    # --- Property Forwarders for Backwards Compatibility ---
    @property
    def var_waze(self) -> tk.BooleanVar:
        return self.sources_section.var_waze

    @property
    def var_tomtom(self) -> tk.BooleanVar:
        return self.sources_section.var_tomtom

    @property
    def var_loop(self) -> tk.BooleanVar:
        return self.sources_section.var_loop

    @property
    def var_camera(self) -> tk.BooleanVar:
        return self.sources_section.var_camera

    @property
    def var_gaps(self) -> tk.BooleanVar:
        return self.problems_section.var_gaps

    @property
    def var_anomalies(self) -> tk.BooleanVar:
        return self.problems_section.var_anomalies

    @property
    def var_duration(self) -> tk.IntVar:
        return self.settings_section.var_duration

    @property
    def var_interval(self) -> tk.IntVar:
        return self.settings_section.var_interval

    @property
    def var_flow_level(self) -> tk.StringVar:
        return self.settings_section.var_flow_level

    @property
    def var_slm_mode(self) -> tk.StringVar:
        return self.settings_section.var_slm_mode

    @property
    def var_num_cameras(self) -> tk.IntVar:
        return self.settings_section.var_num_cameras

    @property
    def var_num_loops(self) -> tk.IntVar:
        return self.settings_section.var_num_loops

    @property
    def var_output_dir(self) -> tk.StringVar:
        return self.output_section.var_output_dir

    @property
    def var_output_name(self) -> tk.StringVar:
        return self.output_section.var_output_name

    @property
    def var_osm_path(self) -> tk.StringVar:
        return self.map_section.var_osm_path

    @property
    def action_button(self) -> Any:
        return self.action_section.action_button

    def on_language_change(self, new_locale: str) -> None:
        """Handles locale switch triggered by the LanguageSection."""
        self.translator.set_locale(new_locale)
        self.update_ui_texts()

    def update_ui_texts(self) -> None:
        """Propagates localization updates across all mounted sections."""
        if isinstance(self.master, tk.Tk):
            self.master.title(self.translator.t("app_title"))

        self.language_section.update_ui_texts(self.translator)
        self.sources_section.update_ui_texts(self.translator)
        self.problems_section.update_ui_texts(self.translator)
        self.settings_section.update_ui_texts(self.translator)
        self.output_section.update_ui_texts(self.translator)
        self.map_section.update_ui_texts(self.translator)
        self.action_section.update_ui_texts(self.translator)

    def set_action_state(self, state: str, text_key: Optional[str] = None) -> None:
        """Sets primary action button state."""
        self.action_section.set_action_state(state, text_key, self.translator)
