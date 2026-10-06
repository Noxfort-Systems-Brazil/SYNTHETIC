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
# File: core/traffic_simulator.py
# Author: Gabriel Moraes
# Date: 2025-11-27

import numpy as np
import datetime
import random
from typing import Dict, Any, Tuple, Optional
from ui.interfaces import IFlowStrategy
from src.core.logger import logger
from src.core.constants import DEFAULT_SPEED_CLAMP_MIN, DEFAULT_SPEED_CLAMP_MAX

class BaseFlowStrategy(IFlowStrategy):
    """
    Base strategy for standard flow calculations (Small, Medium, Large).
    Provides common peak hour and weekday factoring logic.
    """
    def __init__(self, base_amplitude: int, free_flow_speed: int) -> None:
        self.base_amplitude: int = base_amplitude
        self.free_flow_speed: int = free_flow_speed

    def _get_peak_hour_factor(self, hour: float) -> float:
        # Standard morning peak at 8:00, evening peak at 18:00
        peak_morning: float = float(np.exp(-((hour - 8)**2) / (2 * 2**2)))
        peak_evening: float = float(np.exp(-((hour - 18)**2) / (2 * 2.5**2)))
        
        base_level: float = 0.1
        factor: float = base_level + 0.9 * max(peak_morning, peak_evening)
        return factor

    def _get_weekday_factor(self, weekday: int) -> float:
        if weekday < 5: 
            return 1.0
        elif weekday == 5: 
            return 0.7
        else: 
            return 0.5

    def get_ground_truth(self, timestamp: datetime.datetime) -> Dict[str, Any]:
        hour_factor: float = self._get_peak_hour_factor(timestamp.hour + timestamp.minute / 60.0)
        day_factor: float = self._get_weekday_factor(timestamp.weekday())
        
        noise: float = random.uniform(0.90, 1.10)
        current_flow: float = self.base_amplitude * hour_factor * day_factor * noise
        vehicle_count: int = max(0, int(current_flow))

        capacity_factor: float = 2.2
        congestion_metric: float = vehicle_count / (self.base_amplitude * capacity_factor)
        congestion_factor: float = max(0.1, 1.0 - congestion_metric)
        
        current_speed: float = self.free_flow_speed * congestion_factor * noise
        
        return {
            "vehicle_flow": vehicle_count,
            "current_speed": min(max(DEFAULT_SPEED_CLAMP_MIN, int(current_speed)), DEFAULT_SPEED_CLAMP_MAX),
            "free_flow_speed": self.free_flow_speed
        }


class SmallFlowStrategy(BaseFlowStrategy):
    def __init__(self) -> None:
        super().__init__(base_amplitude=30, free_flow_speed=80)


class MediumFlowStrategy(BaseFlowStrategy):
    def __init__(self) -> None:
        super().__init__(base_amplitude=120, free_flow_speed=70)


class LargeFlowStrategy(BaseFlowStrategy):
    def __init__(self) -> None:
        super().__init__(base_amplitude=250, free_flow_speed=60)


class ChaoticFlowStrategy(BaseFlowStrategy):
    """
    Special logic for Chaotic flow, applying standard peak factors
    but maintaining severe congestion close to maximal capacity during peaks.
    """
    def __init__(self) -> None:
        super().__init__(base_amplitude=600, free_flow_speed=50)

    def get_ground_truth(self, timestamp: datetime.datetime) -> Dict[str, Any]:
        hour_factor: float = self._get_peak_hour_factor(timestamp.hour + timestamp.minute / 60.0)
        day_factor: float = self._get_weekday_factor(timestamp.weekday())
        
        # In chaotic, saturation is heavily influenced by the peak factor
        # At 3 AM (hour_factor ~0.1), saturation is much lower.
        base_saturation: float = random.uniform(0.70, 0.90)
        actual_saturation = base_saturation * hour_factor * day_factor
        
        vehicle_count: int = int(self.base_amplitude * actual_saturation)
        
        fluidity: float = max(0.1, 1.0 - actual_saturation)
        current_speed: float = self.free_flow_speed * fluidity
        current_speed = min(max(DEFAULT_SPEED_CLAMP_MIN, int(current_speed)), DEFAULT_SPEED_CLAMP_MAX)

        return {
            "vehicle_flow": vehicle_count,
            "current_speed": current_speed,
            "free_flow_speed": self.free_flow_speed
        }


class DynamicContinuousFlowStrategy(IFlowStrategy):
    """
    Dynamic flow strategy driven by a 48-slot FlowSchedule.
    Interpolates continuously between half-hour steps to guarantee
    physically smooth transitions across:
    Baixo (0) <-> Médio (1) <-> Alto (2) <-> Caótico (3)
    """

    def __init__(self, schedule: Any) -> None:
        from src.core.flow_schedule import FlowSchedule, FlowScheduleValidator
        if isinstance(schedule, FlowSchedule):
            self.schedule = schedule
        else:
            self.schedule = FlowScheduleValidator.parse_from_slm_output(schedule)

    def _interpolate_physical_parameters(self, level: float) -> Tuple[float, int]:
        """
        Maps continuous flow level [0.0, 3.0] to (base_amplitude, free_flow_speed).
        0.0 -> (30 veh/h, 80 km/h)
        1.0 -> (120 veh/h, 70 km/h)
        2.0 -> (250 veh/h, 60 km/h)
        3.0 -> (600 veh/h, 50 km/h)
        """
        level = max(0.0, min(3.0, level))
        
        # Free flow speed drops linearly from 80 km/h to 50 km/h
        free_flow_speed = int(round(80.0 - 10.0 * level))
        
        # Piecewise continuous interpolation of vehicle capacity/amplitude
        if level <= 1.0:
            base_amplitude = 30.0 + 90.0 * level
        elif level <= 2.0:
            base_amplitude = 120.0 + 130.0 * (level - 1.0)
        else:
            base_amplitude = 250.0 + 350.0 * (level - 2.0)
            
        return base_amplitude, free_flow_speed

    def get_ground_truth(self, timestamp: datetime.datetime) -> Dict[str, Any]:
        continuous_level = self.schedule.get_interpolated_level(timestamp)
        base_amplitude, free_flow_speed = self._interpolate_physical_parameters(continuous_level)
        
        noise = random.uniform(0.95, 1.05)
        current_flow = base_amplitude * noise
        vehicle_count = max(0, int(round(current_flow)))
        
        # Congestion factor scales with continuous level
        # At level 3 (chaotic), congestion factor reaches 0.3-0.5
        capacity_metric = continuous_level / 3.0
        congestion_factor = max(0.2, 1.0 - (capacity_metric * 0.7))
        
        current_speed = float(free_flow_speed) * congestion_factor * noise
        clamped_speed = min(max(DEFAULT_SPEED_CLAMP_MIN, int(round(current_speed))), DEFAULT_SPEED_CLAMP_MAX)
        
        return {
            "vehicle_flow": vehicle_count,
            "current_speed": clamped_speed,
            "free_flow_speed": free_flow_speed
        }


class TrafficSimulator:
    """
    The 'Brain' of the simulation context.
    Delegates to a Flow Strategy depending on the level to adhere to OCP.
    """
    
    def __init__(self, strategy: IFlowStrategy) -> None:
        self.strategy: IFlowStrategy = strategy
        logger.info(f"[Cérebro] Inicializado com estratégia: {self.strategy.__class__.__name__}")

    def get_ground_truth(self, timestamp: datetime.datetime) -> Dict[str, Any]:
        return self.strategy.get_ground_truth(timestamp)


class GodunovNetworkFlowStrategy(IFlowStrategy):
    """
    Hydrodynamic flow strategy solving the Lighthill-Whitham-Richards (LWR) PDE
    across a network topology via the cell-to-cell Godunov numerical solver.
    Provides strict vehicle conservation, queue spillback, and shockwave propagation.
    """
    def __init__(
        self,
        topology: Any,
        cfl_factor: float = 0.8,
        incident_manager: Optional[Any] = None,
        signal_controller: Optional[Any] = None
    ) -> None:
        from src.physics.godunov import GodunovSolver
        from src.memory.spatiotemporal_memory import SpatioTemporalMemory
        self.topology = topology
        self.solver = GodunovSolver(topology, cfl_factor=cfl_factor)
        self.incident_manager = incident_manager
        self.signal_controller = signal_controller
        self.memory = SpatioTemporalMemory(num_edges=topology.num_edges, window_size=12)
        
        # Initialize state with 20% capacity baseline
        initial_densities = self.topology.capacities * 0.20 / np.maximum(self.topology.speed_limits_kmh, 10.0)
        self.memory.initialize_state(initial_densities, self.topology.speed_limits_kmh)
        self.last_timestamp: Optional[datetime.datetime] = None

    def step(self, dt_seconds: float, current_time_sec: float, turn_ratios: Optional[Dict[int, Dict[int, float]]] = None) -> Dict[str, Any]:
        curr_dens, _, _, _ = self.memory.get_current_slice()
        turn_ratios = turn_ratios or {}
        
        # Boundary external inflows based on capacity
        external_inflows = np.zeros(self.topology.num_edges, dtype=np.float32)
        for idx in self.topology.inflow_edge_indices:
            external_inflows[idx] = self.topology.capacities[idx] * 0.65

        signal_multipliers = None
        if self.signal_controller:
            signal_multipliers = self.signal_controller.get_all_multipliers(current_time_sec)

        capacity_multipliers = None
        if self.incident_manager:
            capacity_multipliers = np.array([
                self.incident_manager.get_capacity_multiplier(i, current_time_sec)
                for i in range(self.topology.num_edges)
            ], dtype=np.float32)

        new_dens, new_spds, new_flows, new_occs = self.solver.solve_step(
            dt_seconds=dt_seconds,
            current_densities=curr_dens,
            turn_ratios=turn_ratios,
            external_inflows=external_inflows,
            signal_multipliers=signal_multipliers,
            capacity_multipliers=capacity_multipliers
        )
        self.memory.push_step(new_dens, new_spds, new_flows, new_occs)

        mean_spd = float(new_spds.mean()) if len(new_spds) > 0 else 60.0
        clamped_spd = min(max(DEFAULT_SPEED_CLAMP_MIN, int(round(mean_spd))), DEFAULT_SPEED_CLAMP_MAX)
        free_flow = int(round(float(self.topology.speed_limits_kmh.mean()))) if len(self.topology.speed_limits_kmh) > 0 else 60

        return {
            "vehicle_flow": int(round(float(new_flows.sum()))),
            "current_speed": clamped_spd,
            "free_flow_speed": free_flow,
            "mean_density": float(new_dens.mean()),
            "mean_occupancy": float(new_occs.mean()),
            "edge_speeds": new_spds,
            "edge_densities": new_dens,
            "edge_flows": new_flows,
            "edge_occupancies": new_occs,
        }

    def get_ground_truth(self, timestamp: datetime.datetime) -> Dict[str, Any]:
        if self.last_timestamp is None:
            dt = 1.0
        else:
            dt = max(0.1, (timestamp - self.last_timestamp).total_seconds())
        self.last_timestamp = timestamp
        time_sec = float(timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second)
        return self.step(dt_seconds=dt, current_time_sec=time_sec)