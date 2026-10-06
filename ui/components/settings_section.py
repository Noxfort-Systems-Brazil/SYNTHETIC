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
# File: ui/components/settings_section.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict

from ui.interfaces import ITranslator


class SettingsSection(ttk.LabelFrame):
    """
    Visual component for simulation parameters (duration, interval, flow level, SLM mode, sensor counts).
    """

    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, padding="10")
        self.pack(fill="x", expand=True, pady=5)

        self.var_duration: tk.IntVar = tk.IntVar(value=1)
        self.var_interval: tk.IntVar = tk.IntVar(value=10)
        self.var_flow_level: tk.StringVar = tk.StringVar(value="Médio")
        self.var_slm_mode: tk.StringVar = tk.StringVar(value="Realista")

        self.var_num_cameras: tk.IntVar = tk.IntVar(value=5)
        self.var_num_loops: tk.IntVar = tk.IntVar(value=5)

        # Duration Frame
        dur_frame = ttk.Frame(self)
        self.lbl_duration = ttk.Label(dur_frame)
        self.lbl_duration.pack(side="left", padx=5)
        ttk.Entry(dur_frame, textvariable=self.var_duration, width=10).pack(side="left")
        dur_frame.pack(anchor="w")

        # Interval Frame
        int_frame = ttk.Frame(self)
        self.lbl_interval = ttk.Label(int_frame)
        self.lbl_interval.pack(side="left", padx=5)
        ttk.Entry(int_frame, textvariable=self.var_interval, width=10).pack(side="left")
        int_frame.pack(anchor="w", pady=5)

        # Flow Level Frame
        flow_frame = ttk.Frame(self)
        self.lbl_flow_level = ttk.Label(flow_frame)
        self.lbl_flow_level.pack(side="left", padx=5)
        self.rad_flow_small = ttk.Radiobutton(flow_frame, variable=self.var_flow_level, value="Pequeno")
        self.rad_flow_small.pack(side="left")
        self.rad_flow_med = ttk.Radiobutton(flow_frame, variable=self.var_flow_level, value="Médio")
        self.rad_flow_med.pack(side="left")
        self.rad_flow_large = ttk.Radiobutton(flow_frame, variable=self.var_flow_level, value="Grande")
        self.rad_flow_large.pack(side="left")
        self.rad_flow_chaotic = ttk.Radiobutton(flow_frame, variable=self.var_flow_level, value="Caótico")
        self.rad_flow_chaotic.pack(side="left")
        flow_frame.pack(anchor="w", pady=5)

        # SLM Mode Frame
        slm_frame = ttk.Frame(self)
        self.lbl_slm_mode = ttk.Label(slm_frame)
        self.lbl_slm_mode.pack(side="left", padx=5)
        self.rad_slm_ultra = ttk.Radiobutton(slm_frame, variable=self.var_slm_mode, value="Ultrarealista")
        self.rad_slm_ultra.pack(side="left")
        self.rad_slm_real = ttk.Radiobutton(slm_frame, variable=self.var_slm_mode, value="Realista")
        self.rad_slm_real.pack(side="left")
        self.rad_slm_creative = ttk.Radiobutton(slm_frame, variable=self.var_slm_mode, value="Criativo")
        self.rad_slm_creative.pack(side="left")
        slm_frame.pack(anchor="w", pady=5)

        # Local Sensor Configuration Frame
        local_sensors_frame = ttk.Frame(self)
        self.lbl_num_cameras = ttk.Label(local_sensors_frame)
        self.lbl_num_cameras.pack(side="left", padx=5)
        ttk.Entry(local_sensors_frame, textvariable=self.var_num_cameras, width=5).pack(side="left", padx=5)

        self.lbl_num_loops = ttk.Label(local_sensors_frame)
        self.lbl_num_loops.pack(side="left", padx=5)
        ttk.Entry(local_sensors_frame, textvariable=self.var_num_loops, width=5).pack(side="left", padx=5)
        local_sensors_frame.pack(anchor="w", pady=5)

    def get_settings(self) -> Dict[str, Any]:
        """Returns the dictionary of simulation settings."""
        return {
            "duration_days": self.var_duration.get(),
            "interval_seconds": self.var_interval.get(),
            "flow_level": self.var_flow_level.get(),
            "slm_mode": self.var_slm_mode.get(),
            "num_cameras": self.var_num_cameras.get(),
            "num_loops": self.var_num_loops.get(),
        }

    def update_ui_texts(self, translator: ITranslator) -> None:
        """Updates text labels for all configuration inputs."""
        self.config(text=translator.t("section_settings"))
        self.lbl_duration.config(text=translator.t("duration"))
        self.lbl_interval.config(text=translator.t("interval"))
        self.lbl_flow_level.config(text=translator.t("flow_level"))

        self.rad_flow_small.config(text=translator.t("flow_small"))
        self.rad_flow_med.config(text=translator.t("flow_medium"))
        self.rad_flow_large.config(text=translator.t("flow_large"))
        self.rad_flow_chaotic.config(text=translator.t("flow_chaotic"))

        self.lbl_slm_mode.config(text=translator.t("slm_mode"))
        self.rad_slm_ultra.config(text=translator.t("slm_ultra"))
        self.rad_slm_real.config(text=translator.t("slm_real"))
        self.rad_slm_creative.config(text=translator.t("slm_creative"))

        self.lbl_num_cameras.config(text=translator.t("num_cameras"))
        self.lbl_num_loops.config(text=translator.t("num_loops"))
