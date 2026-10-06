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
# File: flow/parser.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import json
import re
from typing import Any, Dict, List, Union
from src.core.logger import logger
from src.core.constants import (
    LEVEL_MAP,
    NUM_SLOTS_PER_DAY
)
from src.flow.model import FlowSchedule


class SLMFlowScheduleParser:
    """
    Specialized parser for extracting 48-slot traffic flow timelines from
    various LLM / SLM response structures.
    """

    @classmethod
    def normalize_level(cls, value: Any) -> int:
        """Converts any string, integer, or float representation into a valid [0..3] level."""
        if isinstance(value, int):
            return max(0, min(3, value))
        if isinstance(value, float):
            return max(0, min(3, int(round(value))))
        if isinstance(value, str):
            clean = value.strip().lower()
            if clean in LEVEL_MAP:
                return LEVEL_MAP[clean]
            for key, val in LEVEL_MAP.items():
                if key in clean:
                    return val
        return 0

    @classmethod
    def extract_slots(cls, slm_output: Union[str, Dict[str, Any], List[Any]]) -> List[int]:
        """
        Extracts raw slot integers from SLM text, dict, or list structures.
        Returns a list of integer levels.
        """
        if not slm_output:
            return []

        parsed_data = slm_output

        # If it's a string, try extracting JSON block or raw JSON
        if isinstance(slm_output, str):
            json_match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', slm_output, re.DOTALL)
            json_str = json_match.group(1) if json_match else None
            
            if not json_str:
                json_match = re.search(r'(\{.*\}|\[.*\])', slm_output, re.DOTALL)
                json_str = json_match.group(1) if json_match else slm_output

            try:
                parsed_data = json.loads(json_str)
            except Exception:
                logger.warning("[SLMFlowScheduleParser] Failed to parse JSON from SLM text.")
                return []

        slots: List[int] = []

        if isinstance(parsed_data, list):
            for item in parsed_data:
                if isinstance(item, dict):
                    level_val = item.get("flow", item.get("level", item.get("value", "baixo")))
                    slots.append(cls.normalize_level(level_val))
                else:
                    slots.append(cls.normalize_level(item))

        elif isinstance(parsed_data, dict):
            for key in ("schedule", "timeline", "flow_levels", "timeline_30min", "slots", "plan"):
                if key in parsed_data and isinstance(parsed_data[key], list):
                    return cls.extract_slots(parsed_data[key])

            if any(":" in str(k) for k in parsed_data.keys()):
                for i in range(NUM_SLOTS_PER_DAY):
                    time_key = FlowSchedule.get_slot_time_str(i)
                    if time_key in parsed_data:
                        val = parsed_data[time_key]
                        if isinstance(val, dict):
                            val = val.get("flow", val.get("level", "baixo"))
                        slots.append(cls.normalize_level(val))
                    else:
                        slots.append(0)

        return slots
