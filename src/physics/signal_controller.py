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
# File: src/physics/signal_controller.py
# Author: Gabriel Moraes
# Date: 2026-10-06

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class SignalPhase:
    duration: float
    state: str

@dataclass
class TrafficLightProgram:
    id: str
    phases: List[SignalPhase] = field(default_factory=list)

    @property
    def total_cycle_time(self) -> float:
        return sum(p.duration for p in self.phases)

    def get_state_at(self, time_sec: float) -> str:
        cycle = self.total_cycle_time
        if cycle <= 0 or not self.phases:
            return ""
        t = time_sec % cycle
        accum = 0.0
        for p in self.phases:
            accum += p.duration
            if t <= accum:
                return p.state
        return self.phases[-1].state

class SignalController:
    """
    Manages physical traffic light schedules, phase transitions, and Riemann flux gating.
    Integrates SUMO tlLogic definitions or creates deterministic alternating cycles.
    """

    def __init__(
        self,
        programs: Optional[Dict[str, TrafficLightProgram]] = None,
        connection_signals: Optional[Dict[Tuple[str, str], Dict[str, Any]]] = None,
        edge_id_to_index: Optional[Dict[str, int]] = None,
        tl_junction_ids: Optional[List[str]] = None
    ):
        self.programs: Dict[str, TrafficLightProgram] = {}
        if programs:
            for tl_id, prog_data in programs.items():
                if isinstance(prog_data, TrafficLightProgram):
                    self.programs[tl_id] = prog_data
                elif isinstance(prog_data, list):
                    sig_phases = [
                        SignalPhase(duration=float(p.get("duration", 30.0)), state=str(p.get("state", "G")))
                        for p in prog_data
                    ]
                    self.programs[tl_id] = TrafficLightProgram(id=tl_id, phases=sig_phases)

        self.connection_signals: Dict[Tuple[str, str], Dict[str, Any]] = connection_signals or {}
        self.edge_id_to_index: Dict[str, int] = edge_id_to_index or {}
        self.tl_junction_ids = set(tl_junction_ids or [])

        # Cache mapped connections by edge indices: (src_idx, dst_idx) -> (tl_id, link_index)
        self.indexed_signals: Dict[Tuple[int, int], Tuple[str, int]] = {}
        for (src_id, dst_id), data in self.connection_signals.items():
            if src_id in self.edge_id_to_index and dst_id in self.edge_id_to_index:
                s_idx = self.edge_id_to_index[src_id]
                d_idx = self.edge_id_to_index[dst_id]
                tl_id = data.get("tl", "")
                link_idx = int(data.get("link_index", 0))
                self.indexed_signals[(s_idx, d_idx)] = (tl_id, link_idx)

    def add_program(self, tl_id: str, phases: List[Dict[str, Any]]):
        sig_phases = [SignalPhase(duration=float(p["duration"]), state=str(p["state"])) for p in phases]
        self.programs[tl_id] = TrafficLightProgram(id=tl_id, phases=sig_phases)

    def get_signal_multiplier(self, src_idx: int, dst_idx: int, current_time_sec: float) -> float:
        """
        Returns fractional flux transmission coefficient in [0.0, 1.0].
        Green ('G', 'g', 'O') = 1.0
        Yellow ('y') = 0.2 (amber clearance)
        Red ('r') = 0.0 (strictly stopped)
        """
        signal_info = self.indexed_signals.get((src_idx, dst_idx))
        if not signal_info:
            return 1.0 # Unsignalized link, free flow

        tl_id, link_idx = signal_info
        prog = self.programs.get(tl_id)

        if prog and prog.phases:
            state = prog.get_state_at(current_time_sec)
            if link_idx < len(state):
                char = state[link_idx]
                if char in ('G', 'g', 'O'):
                    return 1.0
                elif char in ('y', 'Y'):
                    return 0.2
                else:
                    return 0.0
            return 1.0

        # Fallback for traffic_light junctions without explicit SUMO tlLogic:
        # Standard alternating 30s Green / 3s Amber / 30s Red
        cycle = 63.0
        phase_pos = (current_time_sec + src_idx * 15.0) % cycle
        if phase_pos < 30.0:
            return 1.0
        elif phase_pos < 33.0:
            return 0.2
        else:
            return 0.0

    def get_all_multipliers(self, current_time_sec: float) -> Dict[Tuple[int, int], float]:
        """Precomputes signal multipliers for all mapped signalized connections."""
        multipliers: Dict[Tuple[int, int], float] = {}
        for (src_idx, dst_idx) in self.indexed_signals.keys():
            multipliers[(src_idx, dst_idx)] = self.get_signal_multiplier(src_idx, dst_idx, current_time_sec)
        return multipliers
