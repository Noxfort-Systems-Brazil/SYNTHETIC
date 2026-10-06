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
# File: ui/interfaces.py
# Author: Gabriel Moraes
# Date: 2026-08-16

from abc import ABC, abstractmethod
import datetime
from typing import Any, Dict


class IDataGenerator(ABC):
    """
    Interface (Abstract Base Class) that all data generators must implement.
    Enforces the Liskov Substitution Principle (LSP).
    """

    @abstractmethod
    def generate(self, ground_truth: dict, timestamp: datetime.datetime) -> None:
        """
        Generates the data file based on the ground truth.
        """
        pass


class IFlowStrategy(ABC):
    """
    Interface for traffic flow strategies.
    Enforces the Open-Closed Principle (OCP).
    """

    @abstractmethod
    def get_ground_truth(self, timestamp: datetime.datetime) -> dict:
        """
        Calculates the ground truth data for the specific flow level.
        """
        pass


class ITranslator(ABC):
    """
    Interface for UI localization and translation services.
    Enforces the Dependency Inversion Principle (DIP).
    """

    @abstractmethod
    def t(self, key: str, *args: Any) -> str:
        """Translates a given key with optional formatting arguments."""
        pass

    @abstractmethod
    def set_locale(self, locale_code: str) -> None:
        """Switches the active locale."""
        pass

    @abstractmethod
    def get_locale(self) -> str:
        """Returns the active locale code."""
        pass

    @abstractmethod
    def get_supported_locales(self) -> Dict[str, str]:
        """Returns a mapping of {Display Name: Locale Code}."""
        pass