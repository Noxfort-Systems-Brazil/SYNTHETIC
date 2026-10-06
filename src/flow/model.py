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
# File: flow/model.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import datetime
from typing import Dict, List
from src.core.constants import (
    REVERSE_LEVEL_MAP,
    NUM_SLOTS_PER_DAY
)


class FlowSchedule:
    """
    Represents a 24-hour timeline of 48 half-hour slots for traffic flow levels.
    Enforces the bidirectional continuity constraint:
    Baixo (0) <-> Médio (1) <-> Alto (2) <-> Caótico (3)
    """

    def __init__(self, slots: List[int]) -> None:
        if len(slots) != NUM_SLOTS_PER_DAY:
            raise ValueError(f"FlowSchedule requires exactly {NUM_SLOTS_PER_DAY} slots, got {len(slots)}")
        self.slots: List[int] = [max(0, min(3, int(s))) for s in slots]

    @staticmethod
    def get_slot_time_str(slot_idx: int) -> str:
        """Returns the formatted time string (e.g. '08:30') for a given slot index."""
        hours = (slot_idx * 30) // 60
        minutes = (slot_idx * 30) % 60
        return f"{hours:02d}:{minutes:02d}"

    def get_slot_name(self, slot_idx: int) -> str:
        """Returns the text name of the flow level for the given slot."""
        level = self.slots[slot_idx % NUM_SLOTS_PER_DAY]
        return REVERSE_LEVEL_MAP.get(level, "baixo")

    def get_level_at(self, timestamp: datetime.datetime) -> int:
        """Returns the discrete level [0..3] at the given timestamp."""
        slot_idx = (timestamp.hour * 60 + timestamp.minute) // 30
        return self.slots[slot_idx % NUM_SLOTS_PER_DAY]

    def get_interpolated_level(self, timestamp: datetime.datetime) -> float:
        """
        Calculates a smooth continuous level in [0.0, 3.0] by interpolating between
        adjacent 30-minute checkpoints. Uses smoothstep (Hermite interpolation)
        to avoid sharp velocity / flow discontinuities.
        """
        total_seconds = timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second
        slot_exact = total_seconds / 1800.0  # 1800 seconds = 30 minutes
        
        i = int(slot_exact) % NUM_SLOTS_PER_DAY
        j = (i + 1) % NUM_SLOTS_PER_DAY
        alpha = slot_exact - int(slot_exact)

        # Smoothstep curve: s(t) = 3t^2 - 2t^3
        smooth_alpha = alpha * alpha * (3.0 - 2.0 * alpha)

        level_i = float(self.slots[i])
        level_j = float(self.slots[j])

        interpolated = level_i + (level_j - level_i) * smooth_alpha
        return max(0.0, min(3.0, interpolated))

    def to_dict(self) -> Dict[str, str]:
        """Returns a dict mapping 'HH:MM' -> 'level_name'."""
        return {
            self.get_slot_time_str(i): self.get_slot_name(i)
            for i in range(NUM_SLOTS_PER_DAY)
        }

    def to_list(self) -> List[str]:
        """Returns a list of 48 level names."""
        return [self.get_slot_name(i) for i in range(NUM_SLOTS_PER_DAY)]

    def __repr__(self) -> str:
        return f"<FlowSchedule slots={self.slots}>"
