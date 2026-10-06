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
# File: ui/components/sources_section.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import tkinter as tk
from tkinter import ttk
from typing import Dict

from ui.interfaces import ITranslator


class SourcesSection(ttk.LabelFrame):
    """
    Visual component for configuring data sources (Waze, TomTom, Loop, Camera).
    """

    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, padding="10")
        self.pack(fill="x", expand=True)

        self.var_waze: tk.BooleanVar = tk.BooleanVar(value=True)
        self.var_tomtom: tk.BooleanVar = tk.BooleanVar(value=True)
        self.var_loop: tk.BooleanVar = tk.BooleanVar(value=True)
        self.var_camera: tk.BooleanVar = tk.BooleanVar(value=True)

        self.chk_waze = ttk.Checkbutton(self, variable=self.var_waze)
        self.chk_waze.pack(anchor="w")
        self.chk_tomtom = ttk.Checkbutton(self, variable=self.var_tomtom)
        self.chk_tomtom.pack(anchor="w")
        self.chk_loop = ttk.Checkbutton(self, variable=self.var_loop)
        self.chk_loop.pack(anchor="w")
        self.chk_camera = ttk.Checkbutton(self, variable=self.var_camera)
        self.chk_camera.pack(anchor="w")

    def get_sources(self) -> Dict[str, bool]:
        """Returns the dictionary of source enablement states."""
        return {
            "waze": self.var_waze.get(),
            "tomtom": self.var_tomtom.get(),
            "loop": self.var_loop.get(),
            "camera": self.var_camera.get(),
        }

    def update_ui_texts(self, translator: ITranslator) -> None:
        """Updates text labels for all checkboxes and frame header."""
        self.config(text=translator.t("section_sources"))
        self.chk_waze.config(text=translator.t("waze"))
        self.chk_tomtom.config(text=translator.t("tomtom"))
        self.chk_loop.config(text=translator.t("loop"))
        self.chk_camera.config(text=translator.t("camera"))
