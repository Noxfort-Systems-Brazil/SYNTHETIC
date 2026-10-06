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
# File: ui/components/problems_section.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import tkinter as tk
from tkinter import ttk
from typing import Dict

from ui.interfaces import ITranslator


class ProblemsSection(ttk.LabelFrame):
    """
    Visual component for configuring simulated telemetry problems (gaps and anomalies).
    """

    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, padding="10")
        self.pack(fill="x", expand=True, pady=5)

        self.var_gaps: tk.BooleanVar = tk.BooleanVar(value=True)
        self.var_anomalies: tk.BooleanVar = tk.BooleanVar(value=True)

        self.chk_gaps = ttk.Checkbutton(self, variable=self.var_gaps)
        self.chk_gaps.pack(anchor="w")
        self.chk_anomalies = ttk.Checkbutton(self, variable=self.var_anomalies)
        self.chk_anomalies.pack(anchor="w")

    def get_problems(self) -> Dict[str, bool]:
        """Returns the dictionary of problem enablement states."""
        return {
            "gaps": self.var_gaps.get(),
            "anomalies": self.var_anomalies.get(),
        }

    def update_ui_texts(self, translator: ITranslator) -> None:
        """Updates text labels for all problem checkboxes and frame header."""
        self.config(text=translator.t("section_problems"))
        self.chk_gaps.config(text=translator.t("gaps"))
        self.chk_anomalies.config(text=translator.t("anomalies"))
