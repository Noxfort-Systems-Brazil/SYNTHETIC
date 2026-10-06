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
# File: flow/factory.py
# Author: Gabriel Moraes
# Date: 2026-08-16

from src.core.constants import NUM_SLOTS_PER_DAY
from src.flow.model import FlowSchedule
from src.flow.invariants import FlowScheduleInvariantEnforcer


class DefaultScheduleFactory:
    """
    Factory for constructing default, coherent synthetic flow schedules.
    """

    @classmethod
    def create_default(cls, peak_level: int = 2) -> FlowSchedule:
        """
        Creates a coherent synthetic schedule as baseline or fallback:
        - 00:00 - 05:30: Baixo
        - 06:00 - 06:30: Médio (rampa subida manhã)
        - 07:00 - 08:30: Alto / Caótico (pico manhã)
        - 09:00 - 09:30: Médio (rampa descida manhã)
        - 10:00 - 16:30: Médio / Baixo (entre-picos)
        - 17:00 - 19:30: Alto / Caótico (pico tarde)
        - 20:00 - 21:30: Médio (rampa descida tarde)
        - 22:00 - 23:30: Baixo
        """
        peak_level = max(1, min(3, peak_level))
        slots = [0] * NUM_SLOTS_PER_DAY

        # Dawn: 00:00 to 05:30 (slots 0..11) -> 0
        for i in range(12):
            slots[i] = 0

        # Morning ramp: 06:00 (slot 12) -> 1, 06:30 (slot 13) -> min(2, peak_level)
        slots[12] = 1
        slots[13] = min(2, peak_level)
        # Morning peak: 07:00 (14) to 08:30 (17)
        for i in range(14, 18):
            slots[i] = peak_level
        # Morning drop: 09:00 (18) -> min(2, peak_level - 1), 09:30 (19) -> 1
        slots[18] = min(2, max(1, peak_level - 1))
        slots[19] = 1

        # Midday / Afternoon: 10:00 (20) to 16:00 (32)
        for i in range(20, 33):
            if i in (24, 25, 26) and peak_level >= 2:
                slots[i] = 2
            else:
                slots[i] = 1

        # Evening ramp: 16:30 (33) -> min(2, peak_level)
        slots[33] = min(2, peak_level)
        # Evening peak: 17:00 (34) to 19:30 (39)
        for i in range(34, 40):
            slots[i] = peak_level
        # Evening drop: 20:00 (40) -> max(1, peak_level - 1), 20:30 (41) -> 1, 21:00 (42) -> 1, 21:30 (43) -> 1
        slots[40] = min(2, max(1, peak_level - 1))
        slots[41] = 1
        slots[42] = 1
        slots[43] = 1

        # Late night: 22:00 (44) to 23:30 (47) -> 0
        for i in range(44, 48):
            slots[i] = 0

        valid_slots = FlowScheduleInvariantEnforcer.enforce(slots)
        return FlowSchedule(valid_slots)
