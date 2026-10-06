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
# File: src/engine/incident_manager.py
# Author: Gabriel Moraes
# Date: 2026-10-06

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Incident:
    id: str
    edge_id: str
    edge_index: int
    capacity_factor: float # e.g. 0.3 = 70% capacity reduction
    speed_factor: float    # e.g. 0.5 = 50% speed limit reduction
    start_time: float      # simulation seconds when incident began
    duration_seconds: float
    description: str = "Acidente viário"

    def is_active(self, current_time: float) -> bool:
        return self.start_time <= current_time <= (self.start_time + self.duration_seconds)

class IncidentManager:
    """
    Manages live traffic incidents (accidents, construction, lane closures)
    that dynamically modify link capacity and speed limits.
    """

    def __init__(self, edge_id_to_index: Optional[Dict[str, int]] = None):
        self.edge_id_to_index = edge_id_to_index or {}
        self.incidents: Dict[str, Incident] = {}
        self._next_id = 1

    def add_incident(
        self,
        edge_id: str,
        capacity_factor: float = 0.2,
        speed_factor: float = 0.4,
        duration_seconds: float = 600.0,
        start_time: float = 0.0,
        description: str = "Acidente com interdição de faixa"
    ) -> str:
        idx = self.edge_id_to_index.get(edge_id, -1)
        inc_id = f"inc_{self._next_id:04d}"
        self._next_id += 1

        self.incidents[inc_id] = Incident(
            id=inc_id,
            edge_id=edge_id,
            edge_index=idx,
            capacity_factor=capacity_factor,
            speed_factor=speed_factor,
            start_time=start_time,
            duration_seconds=duration_seconds,
            description=description
        )
        return inc_id

    def remove_incident(self, inc_id: str):
        self.incidents.pop(inc_id, None)

    def get_capacity_multiplier(self, edge_idx: int, current_time: float) -> float:
        """Returns capacity multiplier for the given edge index."""
        multiplier = 1.0
        for inc in self.incidents.values():
            if inc.edge_index == edge_idx and inc.is_active(current_time):
                multiplier = min(multiplier, inc.capacity_factor)
        return multiplier

    def get_active_incidents(self, current_time: float) -> List[Dict]:
        """Returns list of currently active incidents for telemetry and UI visualization."""
        return [
            {
                "id": inc.id,
                "edge_id": inc.edge_id,
                "edge_index": inc.edge_index,
                "capacity_factor": inc.capacity_factor,
                "speed_factor": inc.speed_factor,
                "remaining_seconds": max(0.0, (inc.start_time + inc.duration_seconds) - current_time),
                "description": inc.description
            }
            for inc in self.incidents.values()
            if inc.is_active(current_time)
        ]
