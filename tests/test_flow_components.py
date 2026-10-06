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
# File: tests/test_flow_components.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import unittest
from src.flow.model import FlowSchedule
from src.flow.parser import SLMFlowScheduleParser
from src.flow.invariants import FlowScheduleInvariantEnforcer
from src.flow.factory import DefaultScheduleFactory
from src.core.constants import NUM_SLOTS_PER_DAY


class TestFlowComponents(unittest.TestCase):

    def test_parser_normalization(self):
        self.assertEqual(SLMFlowScheduleParser.normalize_level("baixo"), 0)
        self.assertEqual(SLMFlowScheduleParser.normalize_level("médio"), 1)
        self.assertEqual(SLMFlowScheduleParser.normalize_level("alto"), 2)
        self.assertEqual(SLMFlowScheduleParser.normalize_level("caótico"), 3)
        self.assertEqual(SLMFlowScheduleParser.normalize_level(2.8), 3)
        self.assertEqual(SLMFlowScheduleParser.normalize_level(10), 3)
        self.assertEqual(SLMFlowScheduleParser.normalize_level(-5), 0)
        self.assertEqual(SLMFlowScheduleParser.normalize_level("unknown"), 0)

    def test_parser_extraction_from_dict_and_list(self):
        payload_list = ["low", "medium", "high", "chaotic"]
        slots = SLMFlowScheduleParser.extract_slots(payload_list)
        self.assertEqual(slots, [0, 1, 2, 3])

        payload_dict = {"schedule": ["baixo", "médio"]}
        slots = SLMFlowScheduleParser.extract_slots(payload_dict)
        self.assertEqual(slots, [0, 1])

    def test_invariants_enforce(self):
        raw = [3] * NUM_SLOTS_PER_DAY
        slots = FlowScheduleInvariantEnforcer.enforce(raw)
        self.assertEqual(len(slots), NUM_SLOTS_PER_DAY)
        # Dawn clamp
        for i in range(12):
            self.assertEqual(slots[i], 0)
        # Adjacency
        for i in range(NUM_SLOTS_PER_DAY - 1):
            self.assertTrue(abs(slots[i + 1] - slots[i]) <= 1)

    def test_factory_default(self):
        schedule = DefaultScheduleFactory.create_default(peak_level=3)
        self.assertIsInstance(schedule, FlowSchedule)
        self.assertEqual(len(schedule.slots), NUM_SLOTS_PER_DAY)
        self.assertEqual(schedule.slots[0], 0)


if __name__ == "__main__":
    unittest.main()
