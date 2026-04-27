# SYNTHETIC  - An AI-Orchestrated Engine for Multi-Modal Traffic Scenario Synthesis
# Copyright (C) 2026 Noxfort Systems 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# File: agents/screenwriter.py
# Author: Gabriel Moraes
# Date: 2026-02-26

import datetime

class ScreenwriterAgent:
    """
    The Creative Agent of the Synthetic System.
    Translates raw constraints (day of week, time, weather seed, city scale) into a rich,
    semantic prompt for the Cognitive Engine (Qwen).
    Now operates from a MACRO perspective with creative weather interpretation.
    """
    def __init__(self, llm_engine):
        self.llm = llm_engine

    def create_daily_script(self, current_date, constraints: dict) -> dict:
        """
        Drafts the daily scenario prompt and delegates vector synthesis to the LLM.
        """
        # Extract temporal context and physical constraints
        day_of_week = constraints.get('day_of_week', current_date.strftime("%A"))
        start_time = constraints.get('start_time', '00:00:00')
        flow_level = constraints.get('flow_level', 'medium').lower()
        weather_seed = constraints.get('weather', 'Clear')

        # Map the UI flow level to the Macro City Scale context
        city_mapping = {
            "small": "Small City",
            "medium": "Medium City",
            "large": "Metropolis",
            "caotic": "Megalopolis"
        }
        city_size = city_mapping.get(flow_level, "Medium City")

        print(f"[Screenwriter] Drafting MACRO script for {current_date} ({day_of_week}) at {start_time}...")
        print(f"[Screenwriter] Scale: {city_size} | Weather Seed: {weather_seed} | Target Flow: {flow_level.upper()}")

        # The core persona: Shifted from Micro (Driver) to Macro (Omniscient Traffic Network)
        system_instruction = (
            "You are the Synthetic Screenwriter, an expert macro-level traffic network simulator. "
            "Your job is to describe the systemic physical state of an entire city's traffic grid. "
            "DO NOT write from the perspective of a single driver. Think like an omniscient observer "
            "watching the fluid dynamics of thousands of vehicles. Focus strictly on network-wide variables: "
            "overall density, systemic friction, collective braking waves, and macro-level congestion patterns."
        )

        # The specific context for the current simulation chunk with creative freedom
        user_prompt = (
            f"Context: Today is {day_of_week}. The simulation starts exactly at {start_time} (Midnight). "
            f"The environment is a {city_size} with a general traffic flow classification of '{flow_level.upper()}'. "
            f"The initial weather seed for today is '{weather_seed}'. "
            "Treat this weather seed as a starting point. You have the creative, yet realistic, freedom "
            "to imagine exactly how this weather behaves, evolves, or manifests over the hours. "
            "Describe the systemic state of the city's traffic arteries, starting from the eerie calm "
            "of midnight, leading up to the initial build-up of the early morning rush hour. "
            f"Detail exactly how the massive scale of a {city_size} combined with your realistic interpretation "
            f"of the '{weather_seed}' physically impacts the collective movement of the vehicle swarm."
        )

        # Command the LLM to dream the scenario and extract the mathematical vector
        scenario_vector = self.llm.dream_scenario_vector(system_instruction, user_prompt)

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
            "scenario_vector": scenario_vector
        }