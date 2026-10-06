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
# File: tests/test_traffic_simulator.py
# Author: Gabriel Moraes
# Date: 2026-02-26

import unittest
import datetime
from src.core.traffic_simulator import (
    TrafficSimulator,
    SmallFlowStrategy,
    MediumFlowStrategy,
    LargeFlowStrategy,
    ChaoticFlowStrategy,
    DynamicContinuousFlowStrategy
)
from src.core.flow_schedule import FlowScheduleValidator

class TestTrafficSimulator(unittest.TestCase):
    def test_small_flow_strategy(self):
        strategy = SmallFlowStrategy()
        sim = TrafficSimulator(strategy)
        ts = datetime.datetime(2026, 6, 1, 8, 0, 0) # Monday 8 AM (Peak hour)
        res = sim.get_ground_truth(ts)
        self.assertIn("vehicle_flow", res)
        self.assertIn("current_speed", res)
        self.assertIn("free_flow_speed", res)
        self.assertEqual(res["free_flow_speed"], 80)
        self.assertTrue(res["vehicle_flow"] >= 0)

    def test_medium_flow_strategy(self):
        strategy = MediumFlowStrategy()
        sim = TrafficSimulator(strategy)
        ts = datetime.datetime(2026, 6, 1, 12, 0, 0) # Monday noon
        res = sim.get_ground_truth(ts)
        self.assertEqual(res["free_flow_speed"], 70)

    def test_large_flow_strategy(self):
        strategy = LargeFlowStrategy()
        sim = TrafficSimulator(strategy)
        ts = datetime.datetime(2026, 6, 1, 18, 0, 0) # Monday 6 PM (Evening peak)
        res = sim.get_ground_truth(ts)
        self.assertEqual(res["free_flow_speed"], 60)

    def test_chaotic_flow_strategy(self):
        strategy = ChaoticFlowStrategy()
        sim = TrafficSimulator(strategy)
        ts = datetime.datetime(2026, 6, 1, 8, 0, 0)
        res = sim.get_ground_truth(ts)
        self.assertEqual(res["free_flow_speed"], 50)
        self.assertTrue(res["vehicle_flow"] > 0)

    def test_dynamic_continuous_flow_strategy(self):
        schedule = FlowScheduleValidator.create_default_schedule(peak_level=3)
        strategy = DynamicContinuousFlowStrategy(schedule)
        sim = TrafficSimulator(strategy)

        # Dawn test (03:00) -> Baixo
        ts_dawn = datetime.datetime(2026, 6, 1, 3, 0, 0)
        res_dawn = sim.get_ground_truth(ts_dawn)
        self.assertEqual(res_dawn["free_flow_speed"], 80)
        self.assertTrue(res_dawn["vehicle_flow"] <= 60)
        self.assertTrue(res_dawn["current_speed"] >= 60)

        # Peak test (08:00) -> Caótico (level 3)
        ts_peak = datetime.datetime(2026, 6, 1, 8, 0, 0)
        res_peak = sim.get_ground_truth(ts_peak)
        self.assertEqual(res_peak["free_flow_speed"], 50)
        self.assertTrue(res_peak["vehicle_flow"] >= 400)
        self.assertTrue(res_peak["current_speed"] <= 50)

        # Continuity test between 06:00 and 07:30
        ts_6 = datetime.datetime(2026, 6, 1, 6, 0, 0)
        ts_6_30 = datetime.datetime(2026, 6, 1, 6, 30, 0)
        ts_7 = datetime.datetime(2026, 6, 1, 7, 0, 0)
        
        flow_6 = sim.get_ground_truth(ts_6)["vehicle_flow"]
        flow_6_30 = sim.get_ground_truth(ts_6_30)["vehicle_flow"]
        flow_7 = sim.get_ground_truth(ts_7)["vehicle_flow"]
        
        # Ramp should be monotonic upward
        self.assertTrue(flow_6 <= flow_6_30 <= flow_7 + 30)

if __name__ == "__main__":
    unittest.main()

