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
# File: ui/components/output_section.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import os
import tkinter as tk
from tkinter import ttk
from typing import Callable

from ui.interfaces import ITranslator


class OutputSection(ttk.LabelFrame):
    """
    Visual component for output destination directory and folder name selection.
    """

    def __init__(self, parent: ttk.Frame, on_select_output_dir: Callable[[], None]) -> None:
        super().__init__(parent, padding="10")
        self.pack(fill="x", expand=True, pady=5)

        self.on_select_output_dir = on_select_output_dir

        default_output = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.var_output_dir: tk.StringVar = tk.StringVar(value=default_output)
        self.var_output_name: tk.StringVar = tk.StringVar(value="output")

        base_dir_frame = ttk.Frame(self)
        base_dir_frame.pack(fill="x", pady=(0, 5))
        self.output_label = ttk.Label(base_dir_frame, textvariable=self.var_output_dir, relief="sunken")
        self.output_label.pack(fill="x", side="left", expand=True, padx=5)
        self.btn_select_output = ttk.Button(base_dir_frame, command=self.on_select_output_dir)
        self.btn_select_output.pack(side="left")

        folder_name_frame = ttk.Frame(self)
        folder_name_frame.pack(fill="x")
        self.lbl_output_name = ttk.Label(folder_name_frame)
        self.lbl_output_name.pack(side="left", padx=5)
        ttk.Entry(folder_name_frame, textvariable=self.var_output_name).pack(fill="x", side="left", expand=True, padx=5)

    def update_ui_texts(self, translator: ITranslator) -> None:
        """Updates text labels for output selection frame."""
        self.config(text=translator.t("section_output"))
        self.btn_select_output.config(text=translator.t("btn_select"))
        self.lbl_output_name.config(text=translator.t("output_name"))
