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
# File: ui/config_builder.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import os
from typing import Any, Dict, List, Optional
from src.core.map_provider import MapProvider


class SimulationConfigBuilder:
    """
    Builder responsible for validating and assembling the simulation configuration dictionary.
    Decouples GUI form representations from backend simulation parameter specifications.
    """

    @staticmethod
    def build(
        sources: Dict[str, bool],
        problems: Dict[str, bool],
        duration_days: int,
        interval_seconds: int,
        flow_level: str,
        slm_mode: str,
        num_cameras: int,
        num_loops: int,
        base_output_dir: str,
        folder_name: str,
        map_provider: MapProvider,
        cameras: Optional[List[Dict[str, float]]],
        loops: Optional[List[Dict[str, float]]],
    ) -> Dict[str, Any]:
        """
        Validates parameters and builds the nested configuration dictionary expected by the simulator orchestrator.
        """
        clean_folder = folder_name.strip() if folder_name else "output"
        final_output_dir = os.path.join(base_output_dir, clean_folder)

        return {
            "sources": {
                "waze": bool(sources.get("waze", False)),
                "tomtom": bool(sources.get("tomtom", False)),
                "loop": bool(sources.get("loop", False)),
                "camera": bool(sources.get("camera", False)),
            },
            "problems": {
                "gaps": bool(problems.get("gaps", False)),
                "anomalies": bool(problems.get("anomalies", False)),
            },
            "simulation": {
                "duration_days": int(duration_days),
                "interval_seconds": int(interval_seconds),
                "flow_level": str(flow_level),
                "slm_mode": str(slm_mode),
                "num_cameras": int(num_cameras),
                "num_loops": int(num_loops),
            },
            "map": {
                "bounds": map_provider.get_bounds(),
                "provider": map_provider,
                "local_points": {
                    "cameras": cameras or [],
                    "loops": loops or [],
                },
            },
            "output_directory": final_output_dir,
        }
