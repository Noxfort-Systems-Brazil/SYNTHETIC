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
# File: generate_gui.py
# Author: Gabriel Moraes
# Date: 2025-11-27

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os


class DataGeneratorApp(tk.Tk):
    """
    The main Graphical User Interface (GUI) for the Data Generator.
    This is the file you execute.
    """
    def __init__(self):
        super().__init__()

        self.title("SYNTHETIC ")
        
        # --- State Variables ---
        self.var_waze = tk.BooleanVar(value=True)
        self.var_tomtom = tk.BooleanVar(value=True)
        self.var_loop = tk.BooleanVar(value=True)
        self.var_camera = tk.BooleanVar(value=True)

        self.var_gaps = tk.BooleanVar(value=True)
        self.var_anomalies = tk.BooleanVar(value=True)

        # (UPDATED) Changed default to 1 Day
        self.var_duration = tk.IntVar(value=1) 
        self.var_interval = tk.IntVar(value=10)
        # Note: Values kept in Portuguese to match traffic_simulator.py logic
        self.var_flow_level = tk.StringVar(value="Médio") 
        
        self.var_num_cameras = tk.IntVar(value=5)
        self.var_num_loops = tk.IntVar(value=5)
        
        # Set default output directory
        default_output = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        self.var_output_dir = tk.StringVar(value=default_output)

        # --- GUI Layout ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        # --- Section 1: Sources ---
        sources_frame = ttk.LabelFrame(main_frame, text="Data Sources", padding="10")
        sources_frame.pack(fill="x", expand=True)
        
        ttk.Checkbutton(sources_frame, text="Waze (JSON)", variable=self.var_waze).pack(anchor="w")
        ttk.Checkbutton(sources_frame, text="TomTom (JSON)", variable=self.var_tomtom).pack(anchor="w")
        ttk.Checkbutton(sources_frame, text="Inductive Loop (XML)", variable=self.var_loop).pack(anchor="w")
        ttk.Checkbutton(sources_frame, text="Camera (JSON)", variable=self.var_camera).pack(anchor="w")

        # --- Section 2: Problems ---
        problems_frame = ttk.LabelFrame(main_frame, text="Inject Problems", padding="10")
        problems_frame.pack(fill="x", expand=True, pady=5)
        
        ttk.Checkbutton(problems_frame, text="Inject Gaps", variable=self.var_gaps).pack(anchor="w")
        ttk.Checkbutton(problems_frame, text="Inject Anomalies (Noise)", variable=self.var_anomalies).pack(anchor="w")

        # --- Section 3: Settings ---
        config_frame = ttk.LabelFrame(main_frame, text="Simulation Settings", padding="10")
        config_frame.pack(fill="x", expand=True, pady=5)
        
        # Duration (UPDATED TO DAYS)
        dur_frame = ttk.Frame(config_frame)
        ttk.Label(dur_frame, text="Duration (DAYS):").pack(side="left", padx=5)
        ttk.Entry(dur_frame, textvariable=self.var_duration, width=10).pack(side="left")
        dur_frame.pack(anchor="w")
        
        # Interval
        int_frame = ttk.Frame(config_frame)
        ttk.Label(int_frame, text="Interval (seconds):").pack(side="left", padx=5)
        ttk.Entry(int_frame, textvariable=self.var_interval, width=10).pack(side="left")
        int_frame.pack(anchor="w", pady=5)

        # Flow Level (Car Volume)
        flow_frame = ttk.Frame(config_frame)
        ttk.Label(flow_frame, text="Flow Level:").pack(side="left", padx=5)
        ttk.Radiobutton(flow_frame, text="Small", variable=self.var_flow_level, value="Pequeno").pack(side="left")
        ttk.Radiobutton(flow_frame, text="Medium", variable=self.var_flow_level, value="Médio").pack(side="left")
        ttk.Radiobutton(flow_frame, text="Large", variable=self.var_flow_level, value="Grande").pack(side="left")
        ttk.Radiobutton(flow_frame, text="Chaotic", variable=self.var_flow_level, value="Caótico").pack(side="left")
        flow_frame.pack(anchor="w", pady=5)
        
        # Local Sensor Configuration
        local_sensors_frame = ttk.Frame(config_frame)
        
        ttk.Label(local_sensors_frame, text="# of Cameras:").pack(side="left", padx=5)
        ttk.Entry(local_sensors_frame, textvariable=self.var_num_cameras, width=5).pack(side="left", padx=5)
        
        ttk.Label(local_sensors_frame, text="# of Loops:").pack(side="left", padx=5)
        ttk.Entry(local_sensors_frame, textvariable=self.var_num_loops, width=5).pack(side="left", padx=5)
        
        local_sensors_frame.pack(anchor="w", pady=5)

        # --- Section 4: Output Folder ---
        output_frame = ttk.LabelFrame(main_frame, text="Destination Folder (Where 'output' will be created)", padding="10")
        output_frame.pack(fill="x", expand=True, pady=5)
        
        self.output_label = ttk.Label(output_frame, textvariable=self.var_output_dir, relief="sunken")
        self.output_label.pack(fill="x", side="left", expand=True, padx=5)
        ttk.Button(output_frame, text="Select...", command=self.select_output_dir).pack(side="left")

        # --- Section 5: Action ---
        self.action_button = ttk.Button(main_frame, text="GENERATE DATA", command=self.start_generation)
        self.action_button.pack(fill="x", expand=True, ipady=10, pady=10)

    def select_output_dir(self):
        """Opens a dialog box to select the destination folder."""
        directory = filedialog.askdirectory(initialdir=self.var_output_dir.get())
        if directory:
            self.var_output_dir.set(directory)

    def start_generation(self):
        """Starts the generation process in a separate thread."""
        
        # Create final output path
        base_output_dir = self.var_output_dir.get()
        final_output_dir = os.path.join(base_output_dir, "output")

        # 1. Collect all GUI settings
        config = {
            "sources": {
                "waze": self.var_waze.get(),
                "tomtom": self.var_tomtom.get(),
                "loop": self.var_loop.get(),
                "camera": self.var_camera.get(),
            },
            "problems": {
                "gaps": self.var_gaps.get(),
                "anomalies": self.var_anomalies.get(),
            },
            "simulation": {
                # (UPDATED) Changed key to duration_days
                "duration_days": self.var_duration.get(),
                "interval_seconds": self.var_interval.get(),
                "flow_level": self.var_flow_level.get(),
                "num_cameras": self.var_num_cameras.get(),
                "num_loops": self.var_num_loops.get()
            },
            "output_directory": final_output_dir 
        }
        
        # Disable the button
        self.action_button.config(text="Generating...", state="disabled")

        # 2. Start simulation logic in a background thread
        self.generation_thread = threading.Thread(
            target=self.run_simulation_thread,
            args=(config,),
            daemon=True
        )
        self.generation_thread.start()

    def run_simulation_thread(self, config):
        """Executed in the background thread."""
        try:
            # 3. Setup explicitly DIP generators to Orchestrator
            from core.simulation_logic import SimulationOrchestrator
            from globalf.tomtom_generator import TomTomGenerator
            from globalf.waze_generator import WazeGenerator
            from localf.camera_generator import CameraGenerator
            from localf.loop_generator import LoopGenerator
            
            active_generators = []
            if config['sources']['tomtom']: active_generators.append(TomTomGenerator(config))
            if config['sources']['waze']: active_generators.append(WazeGenerator(config))
            if config['sources']['camera']: active_generators.append(CameraGenerator(config))
            if config['sources']['loop']: active_generators.append(LoopGenerator(config))

            orchestrator = SimulationOrchestrator(config, active_generators)
            orchestrator.run()
            
            # 4. Show success
            self.after(0, self.on_generation_complete, config["output_directory"])
        
        except Exception as e:
            # 5. Show error
            self.after(0, self.on_generation_error, e)
            
    def on_generation_complete(self, final_output_dir):
        """Called when generation finishes successfully."""
        messagebox.showinfo("Success", f"Synthetic data generated successfully at:\n{final_output_dir}")
        self.action_button.config(text="GENERATE DATA", state="normal")

    def on_generation_error(self, error):
        """Called if generation fails."""
        print(f"Simulation error: {error}")
        messagebox.showerror("Error", f"An error occurred:\n{error}")
        self.action_button.config(text="GENERATE DATA", state="normal")

if __name__ == "__main__":
    app = DataGeneratorApp()
    app.mainloop()