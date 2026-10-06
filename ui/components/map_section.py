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
# File: ui/components/map_section.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import tkinter as tk
from tkinter import ttk
from typing import Callable

from ui.interfaces import ITranslator


class MapSection(ttk.LabelFrame):
    """
    Visual component for selecting map topology files (.osm, .net.xml).
    """

    def __init__(self, parent: ttk.Frame, on_select_map_file: Callable[[], None]) -> None:
        super().__init__(parent, padding="10")
        self.pack(fill="x", expand=True, pady=5)

        self.on_select_map_file = on_select_map_file
        self.var_osm_path: tk.StringVar = tk.StringVar(value="")

        self.osm_label = ttk.Label(self, textvariable=self.var_osm_path, relief="sunken")
        self.osm_label.pack(fill="x", side="left", expand=True, padx=5)
        self.btn_browse_osm = ttk.Button(self, command=self.on_select_map_file)
        self.btn_browse_osm.pack(side="left")

    def update_ui_texts(self, translator: ITranslator) -> None:
        """Updates text labels for map selection frame."""
        self.config(text=translator.t("section_map"))
        self.btn_browse_osm.config(text=translator.t("btn_browse_osm"))
