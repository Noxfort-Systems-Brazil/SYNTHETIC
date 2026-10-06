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
# File: core/telemetry.py
# Author: Gabriel Moraes
# Date: 2026-06-08

import threading
import time
import subprocess
import os
import psutil
from src.core.logger import logger

class HardwareTelemetry:
    """
    Decoupled service for monitoring hardware resources (RAM/VRAM)
    using psutil and nvidia-smi. Logs specifically to a root directory log file.
    """
    def __init__(self, log_filename: str = "synthetic_slm.log", interval_sec: int = 5):
        # Place log in the root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.log_file = os.path.join(root_dir, log_filename)
        self.interval_sec = interval_sec
        self._running = False
        self._thread = None

    def start(self) -> None:
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
            logger.info(f"[Telemetry] Hardware monitoring started. Logging to {self.log_file}")

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            logger.info("[Telemetry] Hardware monitoring stopped.")

    def _monitor_loop(self) -> None:
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"\n--- Telemetry Session Started at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                while self._running:
                    # RAM Usage
                    ram = psutil.virtual_memory()
                    ram_used_gb = ram.used / (1024**3)
                    ram_total_gb = ram.total / (1024**3)
                    
                    # VRAM Usage via nvidia-smi
                    vram_info = "N/A"
                    try:
                        result = subprocess.run(
                            ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader'],
                            capture_output=True, text=True, check=True
                        )
                        vram_lines = result.stdout.strip().split('\n')
                        if vram_lines:
                            vram_info = " | ".join(vram_lines)
                    except Exception:
                        vram_info = "nvidia-smi not available"
                    
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    log_line = f"[{timestamp}] RAM: {ram_used_gb:.2f}GB / {ram_total_gb:.2f}GB | VRAM: {vram_info}\n"
                    f.write(log_line)
                    f.flush()
                    
                    # Sleep in small increments to allow fast stop
                    for _ in range(self.interval_sec * 10):
                        if not self._running:
                            break
                        time.sleep(0.1)
                        
                f.write(f"--- Telemetry Session Ended at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        except Exception as e:
            logger.error(f"[Telemetry] Loop crashed: {e}")
