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
# File: localf/loop_generator.py
# Author: Gabriel Moraes
# Date: 2026-02-27

import os
import datetime
import random
from core.interfaces import IDataGenerator

class LoopGenerator(IDataGenerator):
    """
    Generates exclusively Inductive Loop data in CSV format.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.output_dir = os.path.join(config['output_directory'], 'loop')
        self.problems = config['problems']
        self.sim_config = config['simulation']
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Quantity configuration
        num_loops = self.sim_config.get('num_loops', 1)
        
        # ID GENERATION
        self.loop_ids = [f"loop_{i:02d}" for i in range(1, num_loops + 1)]

        # Pre-creation of individual folders
        for loop_id in self.loop_ids:
            os.makedirs(os.path.join(self.output_dir, loop_id), exist_ok=True)

    def generate(self, ground_truth: dict, timestamp: datetime.datetime) -> None:
        """Generates CSV counting files for all configured loops."""
        
        # MAESTRO MACRO-GAP CHECK: Abort generation if the physics engine injected a blackout
        if ground_truth.get('vehicle_flow') is None or ground_truth.get('current_speed') is None:
            return

        for sensor_id in self.loop_ids:
            if self.problems['gaps'] and random.random() < 0.10:
                continue

            local_volume_factor = random.uniform(0.04, 0.06)
            vehicle_count = int(ground_truth['vehicle_flow'] * local_volume_factor)
            
            # CSV Header
            csv_content = ["DATA,HORA,ID_SENSOR,FAIXA,CLASSE,VELOCIDADE_KMH,TEMPO_OCUPACAO_MS"]
            
            for _ in range(vehicle_count):
                offset = random.randint(0, 5)
                event_time = timestamp + datetime.timedelta(seconds=offset)
                
                date_str = event_time.strftime("%Y-%m-%d")
                time_str = event_time.strftime("%H:%M:%S")
                
                # Lane Logic: 1 (Fast/Light) vs 2 (Slow/Heavy)
                lane = random.choices([1, 2], weights=[0.6, 0.4])[0]
                
                if lane == 1:
                    v_class = random.choice(["LIGEIRO", "LIGEIRO", "MOTO"])
                    speed = int(ground_truth['current_speed'] * random.uniform(0.95, 1.20))
                else:
                    v_class = random.choice(["LIGEIRO", "PESADO", "PESADO", "ONIBUS"])
                    speed = int(ground_truth['current_speed'] * random.uniform(0.70, 0.95))

                # Physics for Occupancy Time
                length = 4.0 if v_class in ["LIGEIRO", "MOTO"] else 12.0
                speed_ms = max(1, speed / 3.6)
                occupancy = int((length / speed_ms) * 1000)
                
                line = f"{date_str},{time_str},{sensor_id},{lane},{v_class},{speed},{occupancy}"
                csv_content.append(line)

            if self.problems['anomalies'] and random.random() < 0.03:
                csv_content = ["#ERROR: CONTROLLER RESTART", "#DUMP_FAILED"]

            # Save to specific folder: output/loop/loop_XX/file.csv
            ts_string = timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"{sensor_id}_{ts_string}.csv"
            sensor_dir = os.path.join(self.output_dir, sensor_id)
            filepath = os.path.join(sensor_dir, filename)
            
            try:
                with open(filepath, 'w') as f:
                    f.write("\n".join(csv_content))
            except Exception as e:
                print(f"LoopGenerator Error {sensor_id}: {e}")