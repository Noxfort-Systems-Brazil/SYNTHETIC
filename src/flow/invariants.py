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
# File: flow/invariants.py
# Author: Gabriel Moraes
# Date: 2026-08-16

from typing import List
from src.core.constants import NUM_SLOTS_PER_DAY
from src.flow.parser import SLMFlowScheduleParser


class FlowScheduleInvariantEnforcer:
    """
    Enforces physical traffic constraints and continuity rules:
    1. Dawn (00:00 - 05:30, slots 0..11) is strictly Baixo (0).
    2. Late night (22:00 - 23:30, slots 44..47) decodes to Baixo/Médio (<= 1) converging to 0.
    3. Bidirectional adjacency constraint (|L_{t+1} - L_t| <= 1) is never violated.
    """

    @classmethod
    def enforce(cls, raw_slots: List[int]) -> List[int]:
        """
        Enforces all physical bounds and the step-by-step continuity rule:
        |L_{t+1} - L_t| <= 1.
        Returns a list of 48 integer levels [0..3].
        """
        # Ensure we have 48 items
        if len(raw_slots) < NUM_SLOTS_PER_DAY:
            working_slots = list(raw_slots) + [0] * (NUM_SLOTS_PER_DAY - len(raw_slots))
        elif len(raw_slots) > NUM_SLOTS_PER_DAY:
            working_slots = list(raw_slots[:NUM_SLOTS_PER_DAY])
        else:
            working_slots = list(raw_slots)

        slots = [SLMFlowScheduleParser.normalize_level(s) for s in working_slots]

        # 1. Enforce Dawn Hard Bound: 00:00 to 05:30 (slots 0..11) MUST be Baixo (0)
        for i in range(12):
            slots[i] = 0

        # 2. Enforce Late Night Bound: 22:00 to 23:30 (slots 44..47) must decay to 0
        slots[44] = min(slots[44], 1)
        slots[45] = min(slots[45], 1)
        slots[46] = 0
        slots[47] = 0

        # 3. Forward Pass: Enforce |L_{t+1} - L_t| <= 1
        for i in range(NUM_SLOTS_PER_DAY - 1):
            curr_val = slots[i]
            next_val = slots[i + 1]
            if next_val > curr_val + 1:
                slots[i + 1] = curr_val + 1
            elif next_val < curr_val - 1:
                slots[i + 1] = curr_val - 1

        # 4. Backward Pass: Ensure smooth decay into late night and dawn endpoints
        for i in range(NUM_SLOTS_PER_DAY - 1, 0, -1):
            curr_val = slots[i]
            prev_val = slots[i - 1]
            if prev_val > curr_val + 1:
                slots[i - 1] = curr_val + 1

        # Final safety clamp on dawn and late night
        for i in range(12):
            slots[i] = 0
        slots[46] = 0
        slots[47] = 0

        return slots
