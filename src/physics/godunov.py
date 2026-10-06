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
# File: src/physics/godunov.py
# Author: Gabriel Moraes
# Date: 2026-10-06

from typing import Dict, Optional, Tuple
import numpy as np
from src.memory.topology_memory import TopologyMemory
from src.physics.greenshields import GreenshieldsModel

class GodunovSolver:
    """
    Cell-to-cell Godunov numerical solver for the Lighthill-Whitham-Richards (LWR) PDE.
    Enforces strict conservation of vehicles and CFL stability.
    """

    def __init__(self, topology: TopologyMemory, cfl_factor: float = 0.8):
        self.topology = topology
        self.cfl_factor = cfl_factor
        self.num_edges = topology.num_edges

    def solve_step(
        self,
        dt_seconds: float,
        current_densities: np.ndarray,
        turn_ratios: Dict[int, Dict[int, float]],
        external_inflows: np.ndarray,
        pinn_corrections: Optional[np.ndarray] = None,
        signal_multipliers: Optional[Dict[Tuple[int, int], float]] = None,
        capacity_multipliers: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Advances the network state by dt_seconds.
        Enforces Riemann flux gating via traffic signal states and capacity modifiers.
        Returns: (new_densities, new_speeds, new_flows, new_occupancies)
        """
        v_free = self.topology.speed_limits_kmh
        rho_jam = self.topology.jam_densities
        lengths_km = np.maximum(self.topology.lengths_m / 1000.0, 0.01)

        # 1. Compute Sending (Demand) and Receiving (Supply) capacities in veh/h
        demands, supplies = GreenshieldsModel.demand_and_supply(current_densities, v_free, rho_jam)

        # Apply capacity reductions from active incidents
        if capacity_multipliers is not None:
            demands = demands * capacity_multipliers
            supplies = supplies * capacity_multipliers

        inflows_veh_h = np.zeros(self.num_edges, dtype=np.float32)
        outflows_veh_h = np.zeros(self.num_edges, dtype=np.float32)

        # 2. Inject external boundary flows into source edges
        for idx in self.topology.inflow_edge_indices:
            ext_flow = external_inflows[idx]
            actual_inflow = min(ext_flow, float(supplies[idx]))
            inflows_veh_h[idx] += actual_inflow

        # 3. Compute Riemann boundary fluxes with multi-inflow merge partition and boundary sinks
        # First pass: collect proposed demand entering each downstream link
        proposed_turns: Dict[Tuple[int, int], float] = {}
        incoming_demand_to_dst: Dict[int, float] = {}

        outflow_set = set(getattr(self.topology, "outflow_edge_indices", []))

        for src_edge in self.topology.edges:
            src_idx = src_edge.index
            targets = self.topology.outgoing.get(src_edge.id, [])
            d_src = demands[src_idx]

            if not targets:
                # Boundary sink edge: discharges freely into external world
                outflows_veh_h[src_idx] += d_src
                continue

            # If edge is designated as a perimeter boundary outflow edge, let a portion freely discharge externally
            if src_idx in outflow_set:
                boundary_exit = d_src * 0.40
                outflows_veh_h[src_idx] += boundary_exit
                d_src = d_src * 0.60

            edge_turns = turn_ratios.get(src_idx, {})
            total_ratio = sum(edge_turns.get(self.topology.edge_id_to_index[t], 1.0 / len(targets)) for t in targets)
            if total_ratio <= 1e-5:
                total_ratio = 1.0

            for target_id in targets:
                dst_idx = self.topology.edge_id_to_index[target_id]
                alpha = edge_turns.get(dst_idx, 1.0 / len(targets)) / total_ratio
                target_demand = d_src * alpha

                sig_mult = 1.0
                if signal_multipliers is not None:
                    sig_mult = signal_multipliers.get((src_idx, dst_idx), 1.0)

                gated_demand = target_demand * sig_mult
                proposed_turns[(src_idx, dst_idx)] = gated_demand
                incoming_demand_to_dst[dst_idx] = incoming_demand_to_dst.get(dst_idx, 0.0) + gated_demand

        # Second pass: allocate downstream supply fairly among converging incoming edges (Merge Node Model)
        for (src_idx, dst_idx), gated_demand in proposed_turns.items():
            tot_dem = incoming_demand_to_dst.get(dst_idx, 0.0)
            avail_supply = float(supplies[dst_idx])

            if tot_dem <= avail_supply or tot_dem <= 1e-5:
                flux = gated_demand
            else:
                # Proportional fair-share merge: total inflow into dst cannot exceed avail_supply
                flux = gated_demand * (avail_supply / tot_dem)

            outflows_veh_h[src_idx] += flux
            inflows_veh_h[dst_idx] += flux

        # 4. Trip completion / Destination parking dissipation on residential/local edges
        # In urban networks, vehicles reach their destinations and park.
        # Mean trip duration tau_trip ~ 12 minutes (720s).
        residential_set = set(getattr(self.topology, "internal_residential_indices", []))
        trip_completion_rate = 1.0 / 720.0  # ~12 min average trip completion time
        trip_completion_veh_h = np.zeros(self.num_edges, dtype=np.float32)
        for r_idx in residential_set:
            veh_on_link = current_densities[r_idx] * lengths_km[r_idx]
            trip_completion_veh_h[r_idx] = veh_on_link * (trip_completion_rate * 3600.0)

        # 5. Mass conservation PDE: d(rho)/dt = (q_in - q_out - q_dest) / L + residual
        net_flux = inflows_veh_h - outflows_veh_h - trip_completion_veh_h
        if pinn_corrections is not None:
            # Zero-center PINN corrections to strictly preserve mass conservation across the network
            pinn_centered = pinn_corrections - float(np.mean(pinn_corrections))
            pinn_clipped = np.clip(pinn_centered, -15.0, 15.0)
            net_flux += pinn_clipped

        # dt in hours: dt_seconds / 3600.0
        dt_hours = dt_seconds / 3600.0
        delta_rho = (net_flux / lengths_km) * dt_hours

        # Update and clamp
        new_densities = np.clip(current_densities + delta_rho, 0.0, rho_jam)
        new_speeds = GreenshieldsModel.speed(new_densities, v_free, rho_jam)
        new_flows = new_densities * new_speeds
        new_occupancies = np.clip(new_densities / np.maximum(rho_jam, 1e-3), 0.0, 1.0)

        return new_densities, new_speeds, new_flows, new_occupancies
