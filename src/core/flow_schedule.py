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
# File: core/flow_schedule.py
# Author: Gabriel Moraes
# Date: 2026-08-16

from typing import Any, Dict, List, Union
from src.core.logger import logger
from src.flow.model import FlowSchedule
from src.flow.parser import SLMFlowScheduleParser
from src.flow.invariants import FlowScheduleInvariantEnforcer
from src.flow.factory import DefaultScheduleFactory

__all__ = [
    "FlowSchedule",
    "FlowScheduleValidator",
    "SLMFlowScheduleParser",
    "FlowScheduleInvariantEnforcer",
    "DefaultScheduleFactory",
]


class FlowScheduleValidator:
    """
    Pure Orchestrator / Facade for parsing, validating, and instantiating FlowSchedule.
    Coordinates specialized components:
    - Parser: SLMFlowScheduleParser (extracts and normalizes raw inputs)
    - Invariants: FlowScheduleInvariantEnforcer (enforces physical continuity & bounds)
    - Factory: DefaultScheduleFactory (generates baseline / fallback profiles)
    """

    @classmethod
    def normalize_level(cls, value: Any) -> int:
        """Normalizes any input representation into a valid discrete level [0..3]."""
        return SLMFlowScheduleParser.normalize_level(value)

    @classmethod
    def create_default_schedule(cls, peak_level: int = 2) -> FlowSchedule:
        """Creates a coherent synthetic baseline schedule."""
        return DefaultScheduleFactory.create_default(peak_level=peak_level)

    @classmethod
    def enforce_invariants(cls, raw_slots: List[int]) -> FlowSchedule:
        """Enforces physical bounds and bidirectional continuity |L_{t+1} - L_t| <= 1."""
        valid_slots = FlowScheduleInvariantEnforcer.enforce(raw_slots)
        return FlowSchedule(valid_slots)

    @classmethod
    def parse_from_slm_output(
        cls,
        slm_output: Union[str, Dict[str, Any], List[Any]],
        fallback_peak_level: int = 2
    ) -> FlowSchedule:
        """
        Orchestrates the end-to-end extraction, validation, and construction
        of a FlowSchedule from SLM responses or fallback configurations.
        """
        if not slm_output:
            return cls.create_default_schedule(fallback_peak_level)

        slots = SLMFlowScheduleParser.extract_slots(slm_output)

        if len(slots) >= 12:
            return cls.enforce_invariants(slots)

        logger.warning(f"[FlowScheduleValidator] Insufficient slots ({len(slots)}). Generating baseline schedule.")
        return cls.create_default_schedule(fallback_peak_level)
