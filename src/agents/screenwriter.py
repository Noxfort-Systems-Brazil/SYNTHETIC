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
# File: agents/screenwriter.py
# Author: Gabriel Moraes
# Date: 2026-02-26

import os
import json
import datetime
from typing import Dict, Any, Optional
from src.core.logger import logger

class ScreenwriterAgent:
    """
    The Creative Agent of the Synthetic System.
    Translates raw constraints (day of week, time, weather seed, city scale) into a rich,
    semantic prompt for the Cognitive Engine (Qwen).
    Now operates from a MACRO perspective with creative weather interpretation,
    externalizing templates and mappings into a JSON configuration to respect OCP.
    """
    def __init__(self, llm_engine: Any, config_path: Optional[str] = None) -> None:
        self.llm: Any = llm_engine
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            config_path = os.path.join(base_dir, "prompt", "screenwriter.json")
        self.config: Dict[str, Any] = self._load_config(config_path)

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Loads screenwriter configuration and prompt templates from JSON."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, PermissionError) as e:
            logger.error(f"[Screenwriter] Config file not found or inaccessible at '{path}': {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"[Screenwriter] Config file corrupted at '{path}': {e}")
            return {}

    def create_daily_script(self, current_date: datetime.date, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Drafts the daily scenario prompt and delegates vector synthesis to the LLM.
        """
        english_days = self.config.get(
            "english_days",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        )
        day_of_week: str = constraints.get('day_of_week', english_days[current_date.weekday()])
        
        start_time: str = constraints.get('start_time', '00:00:00')
        flow_level: str = constraints.get('flow_level', 'medium').lower()
        weather_seed: str = constraints.get('weather', 'Clear')

        # Map the UI flow level (PT-BR or EN) to the Macro City Scale context
        city_mapping = self.config.get("city_mapping", {})
        city_size: str = city_mapping.get(flow_level, "Medium City")

        flow_translation = self.config.get("flow_translation", {})
        english_flow: str = flow_translation.get(flow_level, "medium")

        logger.info(f"[Screenwriter] Drafting MACRO script for {current_date} ({day_of_week}) at {start_time}...")
        logger.info(f"[Screenwriter] Scale: {city_size} | Weather Seed: {weather_seed} | Target Flow: {english_flow.upper()}")

        # The core persona
        system_instruction: str = self.config.get("system_instruction", "")

        # The specific context for the current simulation chunk with creative freedom
        previous_weather: Optional[str] = constraints.get('previous_weather', None)
        transition_context: str = ""
        weather_transitions = self.config.get("weather_transitions", {})

        if previous_weather:
            if previous_weather == weather_seed:
                template = weather_transitions.get(
                    "persisting",
                    "The weather from yesterday ('{previous_weather}') persists into today, carrying over its physical effects on the infrastructure. "
                )
                transition_context = template.format(previous_weather=previous_weather)
            else:
                template = weather_transitions.get(
                    "changing",
                    "Yesterday the city experienced '{previous_weather}'. Today, this transitions into '{weather_seed}'. Consider how the aftermath of yesterday's weather impacts today's initial conditions. "
                )
                transition_context = template.format(previous_weather=previous_weather, weather_seed=weather_seed)
        
        next_weather_forecast: Optional[str] = constraints.get('next_weather_forecast', None)
        forecast_context: str = ""
        if next_weather_forecast:
            template_forecast = weather_transitions.get(
                "forecast",
                "Tomorrow's meteorological trend forecast is '{next_weather_forecast}'. "
            )
            forecast_context = template_forecast.format(next_weather_forecast=next_weather_forecast)

        user_prompt_template: str = self.config.get("user_prompt_template", "")
        user_prompt: str = user_prompt_template.format(
            day_of_week=day_of_week,
            start_time=start_time,
            city_size=city_size,
            english_flow=english_flow.upper(),
            transition_context=transition_context,
            forecast_context=forecast_context,
            weather_seed=weather_seed
        )


        from src.core.flow_schedule import FlowScheduleValidator
        from src.core.constants import LEVEL_MAP

        # Determine target peak level for fallback/validation
        target_peak = LEVEL_MAP.get(english_flow.lower(), 2)

        # Command the LLM to dream the scenario and extract both the vector and payload
        if hasattr(self.llm, "dream_daily_scenario"):
            dream_result = self.llm.dream_daily_scenario(system_instruction, user_prompt)
            scenario_vector = dream_result.get("vector", [])
            raw_text = dream_result.get("raw_text", "")
            flow_schedule = FlowScheduleValidator.parse_from_slm_output(raw_text, fallback_peak_level=target_peak)
        else:
            scenario_vector = self.llm.dream_scenario_vector(system_instruction, user_prompt)
            flow_schedule = FlowScheduleValidator.create_default_schedule(peak_level=target_peak)

        logger.info(f"[Screenwriter] 48-slot Flow Schedule generated. Morning Peak: {flow_schedule.get_slot_name(15)} | Evening Peak: {flow_schedule.get_slot_name(36)}")

        # Return the package to the Maestro
        return {
            "date": str(current_date),
            "metadata": {
                "day_of_week": day_of_week,
                "weather": weather_seed,
                "flow_level": flow_level,
                "city_size": city_size,
                "start_time": start_time
            },
            "scenario_vector": scenario_vector,
            "flow_schedule": flow_schedule
        }