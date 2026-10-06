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
# File: tests/test_physics_godunov.py
# Author: Gabriel Moraes
# Date: 2026-10-06

import unittest
import numpy as np
import datetime

from src.physics.greenshields import GreenshieldsModel
from src.physics.godunov import GodunovSolver
from src.physics.shockwave import ShockwaveAnalyzer
from src.physics.signal_controller import SignalController, SignalPhase, TrafficLightProgram
from src.physics.centroid_analyzer import CentroidAnalyzer
from src.physics.geo_projection import GeoProjection
from src.memory.topology_memory import TopologyMemory, RoadEdge
from src.engine.incident_manager import IncidentManager
from src.core.traffic_simulator import TrafficSimulator, GodunovNetworkFlowStrategy

class TestPhysicsGodunov(unittest.TestCase):
    def setUp(self):
        # Build minimal synthetic 3-edge corridor: Edge 0 -> Edge 1 -> Edge 2
        self.edges = [
            RoadEdge(id="e0", index=0, from_node="n0", to_node="n1", num_lanes=2, length_m=200.0, speed_limit_kmh=60.0, capacity_veh_per_hour=1800.0, jam_density_veh_km=140.0, coordinates=[(-23.55, -46.65), (-23.54, -46.64)], shape=[(0.0, 0.0), (200.0, 0.0)]),
            RoadEdge(id="e1", index=1, from_node="n1", to_node="n2", num_lanes=2, length_m=200.0, speed_limit_kmh=60.0, capacity_veh_per_hour=1800.0, jam_density_veh_km=140.0, coordinates=[(-23.54, -46.64), (-23.53, -46.63)], shape=[(200.0, 0.0), (400.0, 0.0)]),
            RoadEdge(id="e2", index=2, from_node="n2", to_node="n3", num_lanes=2, length_m=200.0, speed_limit_kmh=60.0, capacity_veh_per_hour=1800.0, jam_density_veh_km=140.0, coordinates=[(-23.53, -46.63), (-23.52, -46.62)], shape=[(400.0, 0.0), (600.0, 0.0)]),
        ]
        self.connections = [("e0", "e1"), ("e1", "e2")]
        self.topology = TopologyMemory(self.edges, self.connections)

    def test_greenshields_fundamental_diagram(self):
        density = np.array([0.0, 70.0, 140.0], dtype=np.float32)
        v_free = np.array([60.0, 60.0, 60.0], dtype=np.float32)
        rho_jam = np.array([140.0, 140.0, 140.0], dtype=np.float32)

        speeds = GreenshieldsModel.speed(density, v_free, rho_jam)
        flows = GreenshieldsModel.flow(density, v_free, rho_jam)

        self.assertAlmostEqual(speeds[0], 60.0, places=2)
        self.assertAlmostEqual(flows[0], 0.0, places=2)
        self.assertAlmostEqual(speeds[1], 30.0, places=2)
        self.assertAlmostEqual(flows[1], 2100.0, places=2)
        self.assertAlmostEqual(speeds[2], 0.0, places=2)
        self.assertAlmostEqual(flows[2], 0.0, places=2)

    def test_godunov_conservation_and_bounds(self):
        solver = GodunovSolver(self.topology)
        curr_dens = np.array([20.0, 20.0, 20.0], dtype=np.float32)
        turn_ratios = {0: {1: 1.0}, 1: {2: 1.0}}
        inflows = np.array([500.0, 0.0, 0.0], dtype=np.float32)

        new_dens, new_spds, new_flows, new_occs = solver.solve_step(
            dt_seconds=1.0,
            current_densities=curr_dens,
            turn_ratios=turn_ratios,
            external_inflows=inflows
        )

        self.assertTrue(np.all(new_dens >= 0.0))
        self.assertTrue(np.all(new_dens <= self.topology.jam_densities))
        self.assertTrue(np.all(new_spds >= 0.0))
        self.assertTrue(np.all(new_spds <= self.topology.speed_limits_kmh + 1e-2))

    def test_shockwave_analyzer(self):
        rho1, q1 = 20.0, 1000.0
        rho2, q2 = 100.0, 500.0
        w = ShockwaveAnalyzer.wave_speed(rho1, q1, rho2, q2)
        self.assertLess(w, 0.0)
        self.assertAlmostEqual(w, -6.25, places=2)

    def test_signal_controller_gating(self):
        phases = [SignalPhase(duration=30.0, state="G"), SignalPhase(duration=30.0, state="r")]
        prog = TrafficLightProgram(id="tl1", phases=phases)
        signals = {("e0", "e1"): {"tl": "tl1", "link_index": 0}}
        sc = SignalController(programs={"tl1": prog}, connection_signals=signals, edge_id_to_index=self.topology.edge_id_to_index)

        # At t=10s: Green
        mult_green = sc.get_signal_multiplier(0, 1, 10.0)
        self.assertEqual(mult_green, 1.0)

        # At t=40s: Red
        mult_red = sc.get_signal_multiplier(0, 1, 40.0)
        self.assertEqual(mult_red, 0.0)

    def test_incident_manager_capacity_drop(self):
        im = IncidentManager(self.topology.edge_id_to_index)
        inc_id = im.add_incident("e1", capacity_factor=0.3, speed_factor=0.5, start_time=100.0, duration_seconds=600.0)

        # Inactive before start
        self.assertEqual(im.get_capacity_multiplier(1, 50.0), 1.0)
        # Active during incident
        self.assertEqual(im.get_capacity_multiplier(1, 200.0), 0.3)
        # Inactive after duration
        self.assertEqual(im.get_capacity_multiplier(1, 800.0), 1.0)

    def test_godunov_network_flow_strategy(self):
        strategy = GodunovNetworkFlowStrategy(self.topology)
        sim = TrafficSimulator(strategy)
        ts = datetime.datetime(2026, 6, 1, 8, 0, 0)
        gt = sim.get_ground_truth(ts)

        self.assertIn("vehicle_flow", gt)
        self.assertIn("current_speed", gt)
        self.assertIn("edge_speeds", gt)
        self.assertIn("edge_densities", gt)
        self.assertEqual(len(gt["edge_speeds"]), 3)
        self.assertTrue(gt["current_speed"] > 0)

if __name__ == "__main__":
    unittest.main()
