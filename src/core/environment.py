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
# File: core/environment.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import datetime
import random
import json
import os
from typing import Optional, Tuple, List, Dict, Any


class EnvironmentManager:
    """
    Manages the physical constraints and passage of time in the simulation.
    Handles the start time and the realistic evolution of atmospheric conditions
    via a stochastic Markov Chain with day-to-day temporal continuity.
    """
    
    _weather_rules: Optional[Dict[str, Any]] = None

    @classmethod
    def _load_weather_rules(cls) -> Dict[str, Any]:
        if cls._weather_rules is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "weather_rules.json")
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cls._weather_rules = json.load(f)
            except (FileNotFoundError, PermissionError) as e:
                from src.core.logger import logger
                logger.error(f"[Environment] Weather configuration file not found or inaccessible: {e}")
                cls._weather_rules = {}
            except json.JSONDecodeError as e:
                from src.core.logger import logger
                logger.error(f"[Environment] Weather rules file corrupted: {e}")
                cls._weather_rules = {}
        return cls._weather_rules or {}

    @staticmethod
    def get_next_monday_midnight() -> datetime.datetime:
        """
        Calculates the exact datetime for the upcoming Monday at 00:00:00.
        Acts as the 'Ground Zero' for the traffic cycle.
        """
        now: datetime.datetime = datetime.datetime.now()
        midnight_today: datetime.datetime = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        days_ahead: int = 0 - midnight_today.weekday()
        if days_ahead <= 0: 
            days_ahead += 7
            
        return midnight_today + datetime.timedelta(days=days_ahead)

    @classmethod
    def _format_weather_string(cls, state: Tuple[str, str, str]) -> str:
        """Formats a weather tuple (intensity, condition, characteristics) into a natural English string."""
        rules = cls._load_weather_rules()
        category_map = rules.get("category_map", {})
        intensity, cond, char = state
        cat = category_map.get(cond, "Clear/Cloudy")

        if cat == "Clear/Cloudy":
            return f"{cond} {char}".strip()
        return f"{intensity.capitalize()} {cond.lower()} {char}".strip()

    @classmethod
    def sample_next_condition(cls, prev_cond: Optional[str] = None) -> str:
        """Samples the next atmospheric condition using the weighted Markov Transition Matrix."""
        rules = cls._load_weather_rules()
        weighted_transitions = rules.get("transitions_weighted", {})
        transitions = rules.get("transitions", {})
        initial_states = rules.get("initial_states", ["Partly Cloudy"])
        initial_weights = rules.get("initial_weights", [100])

        if prev_cond is None:
            return random.choices(initial_states, weights=initial_weights, k=1)[0]

        # 1. Try weighted transition matrix first
        if prev_cond in weighted_transitions:
            options_dict = weighted_transitions[prev_cond]
            states = list(options_dict.keys())
            weights = list(options_dict.values())
            return random.choices(states, weights=weights, k=1)[0]

        # 2. Fallback to unweighted list
        if prev_cond in transitions:
            return random.choice(transitions[prev_cond])

        return "Partly Cloudy"

    @classmethod
    def get_dynamic_weather(cls, weather_state: Optional[Tuple[str, str, str]] = None) -> Tuple[Tuple[str, str, str], str]:
        """
        Provides a realistic atmospheric seed using a stochastic Markov Chain.
        Evolves weather logically from the previous day's state (S_t-1 -> S_t)
        with weighted probabilistic transitions.
        """
        rules = cls._load_weather_rules()
        category_map = rules.get("category_map", {})
        intensity_map = rules.get("intensity_map", {"Clear/Cloudy": ["mild"], "Precipitation": ["light"], "Extreme": ["severe"]})
        char_map = rules.get("char_map", {})

        prev_cond = weather_state[1] if weather_state else None
        cond = cls.sample_next_condition(prev_cond)

        cat = category_map.get(cond, "Clear/Cloudy")
        intensity = random.choice(intensity_map.get(cat, ["mild"]))
        char = random.choice(char_map.get(cond, [""]))

        new_state: Tuple[str, str, str] = (intensity, cond, char)
        weather_str = cls._format_weather_string(new_state)

        return new_state, weather_str

    @classmethod
    def peek_next_weather(cls, current_state: Optional[Tuple[str, str, str]] = None) -> Tuple[Tuple[str, str, str], str]:
        """
        Samples a prospective forecast for the following day (S_t -> S_t+1)
        without mutating the current simulation state.
        """
        return cls.get_dynamic_weather(current_state)

    @classmethod
    def generate_weather_chain(cls, num_days: int, initial_state: Optional[Tuple[str, str, str]] = None) -> List[Tuple[Tuple[str, str, str], str]]:
        """
        Generates a contiguous multi-day Markov Chain of weather states [Day_0, Day_1, ..., Day_{N-1}].
        Guarantees temporal continuity across all days of the simulation.
        """
        chain: List[Tuple[Tuple[str, str, str], str]] = []
        state = initial_state

        for _ in range(max(1, num_days)):
            state, weather_str = cls.get_dynamic_weather(state)
            chain.append((state, weather_str))

        return chain
