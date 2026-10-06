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
# File: tests/test_flow_schedule.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import unittest
import datetime
import json
from src.core.flow_schedule import (
    FlowSchedule,
    FlowScheduleValidator
)
from src.core.constants import (
    NUM_SLOTS_PER_DAY,
    LEVEL_MAP
)



class TestFlowSchedule(unittest.TestCase):

    def test_default_schedule_structure(self):
        schedule = FlowScheduleValidator.create_default_schedule(peak_level=2)
        self.assertEqual(len(schedule.slots), NUM_SLOTS_PER_DAY)
        
        # Dawn: 00:00 to 05:30 (slots 0..11) MUST be Baixo (0)
        for i in range(12):
            self.assertEqual(schedule.slots[i], 0, f"Slot {i} ({schedule.get_slot_time_str(i)}) should be 0 (Baixo)")

        # Late night: 23:00 to 23:30 (slots 46, 47) MUST be Baixo (0)
        self.assertEqual(schedule.slots[46], 0)
        self.assertEqual(schedule.slots[47], 0)

        # Adjacency continuity: |L_{i+1} - L_i| <= 1
        for i in range(NUM_SLOTS_PER_DAY - 1):
            diff = abs(schedule.slots[i + 1] - schedule.slots[i])
            self.assertTrue(diff <= 1, f"Discontinuous jump at slot {i}->{i+1}: {schedule.slots[i]} to {schedule.slots[i+1]}")

    def test_enforce_invariants_clamps_illegal_jump(self):
        # Attempt to jump straight from 0 to 3 at slot 12
        raw_slots = [0] * 12 + [3] * 36
        schedule = FlowScheduleValidator.enforce_invariants(raw_slots)

        self.assertEqual(len(schedule.slots), NUM_SLOTS_PER_DAY)
        
        # Check that jump was smoothed: slot 12 can be at most 1, slot 13 at most 2, slot 14 at most 3
        self.assertEqual(schedule.slots[11], 0)
        self.assertEqual(schedule.slots[12], 1)
        self.assertEqual(schedule.slots[13], 2)
        self.assertEqual(schedule.slots[14], 3)

        # Check all adjacency constraints
        for i in range(NUM_SLOTS_PER_DAY - 1):
            diff = abs(schedule.slots[i + 1] - schedule.slots[i])
            self.assertTrue(diff <= 1, f"Discontinuous step at {i}: {schedule.slots[i]} -> {schedule.slots[i+1]}")

    def test_parse_from_slm_json_schedule(self):
        slm_payload = {
            "scenario_description": "Traffic builds up progressively during morning rush hour.",
            "schedule": ["low"] * 12 + ["medium", "high", "high", "high", "medium"] + ["medium"] * 31
        }
        json_str = f"Here is the plan:\n```json\n{json.dumps(slm_payload)}\n```\nHope this helps!"
        schedule = FlowScheduleValidator.parse_from_slm_output(json_str)

        self.assertEqual(len(schedule.slots), NUM_SLOTS_PER_DAY)
        self.assertEqual(schedule.slots[0], 0)
        self.assertEqual(schedule.slots[12], 1)
        self.assertEqual(schedule.slots[13], 2)

    def test_parse_from_time_map(self):
        time_map = {
            "00:00": "baixo",
            "06:00": "médio",
            "07:00": "alto",
            "08:00": "caótico",
            "18:00": "caótico",
            "23:30": "baixo"
        }
        schedule = FlowScheduleValidator.parse_from_slm_output(time_map)
        self.assertEqual(len(schedule.slots), NUM_SLOTS_PER_DAY)
        # Verify continuity is guaranteed
        for i in range(NUM_SLOTS_PER_DAY - 1):
            diff = abs(schedule.slots[i + 1] - schedule.slots[i])
            self.assertTrue(diff <= 1)

    def test_continuous_interpolation(self):
        # Create a schedule with a valid progressive ramp
        slots = [0] * NUM_SLOTS_PER_DAY
        slots[12] = 1  # 06:00 -> 1 (Médio)
        slots[13] = 2  # 06:30 -> 2 (Alto)
        slots[14] = 2  # 07:00 -> 2 (Alto)
        slots[15] = 3  # 07:30 -> 3 (Caótico)
        schedule = FlowScheduleValidator.enforce_invariants(slots)


        # At 07:00 exactly
        t0 = datetime.datetime(2026, 6, 1, 7, 0, 0)
        lvl0 = schedule.get_interpolated_level(t0)
        self.assertAlmostEqual(lvl0, float(schedule.slots[14]), delta=0.01)

        # At 07:15 (halfway between 07:00 and 07:30)
        t_mid = datetime.datetime(2026, 6, 1, 7, 15, 0)
        lvl_mid = schedule.get_interpolated_level(t_mid)
        self.assertTrue(schedule.slots[14] <= lvl_mid <= schedule.slots[15])
        self.assertAlmostEqual(lvl_mid, 2.5, delta=0.1)

        # At 07:30 exactly
        t1 = datetime.datetime(2026, 6, 1, 7, 30, 0)
        lvl1 = schedule.get_interpolated_level(t1)
        self.assertAlmostEqual(lvl1, float(schedule.slots[15]), delta=0.01)

    def test_to_dict_and_to_list(self):
        schedule = FlowScheduleValidator.create_default_schedule()
        d = schedule.to_dict()
        self.assertEqual(len(d), NUM_SLOTS_PER_DAY)
        self.assertIn("00:00", d)
        self.assertIn("23:30", d)

        lst = schedule.to_list()
        self.assertEqual(len(lst), NUM_SLOTS_PER_DAY)
        self.assertEqual(lst[0], "baixo")


if __name__ == "__main__":
    unittest.main()
