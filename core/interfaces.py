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
# File: interfaces.py
# Author: Gabriel Moraes
# Date: 2025-11-27

from abc import ABC, abstractmethod
import datetime

class IDataGenerator(ABC):
    """
    Interface (Abstract Base Class) that all data generators must implement.
    
    This enforces the Liskov Substitution Principle (LSP): any class inheriting
    from this interface can be used interchangeably in the simulation logic
    without breaking the system.
    """

    @abstractmethod
    def generate(self, ground_truth: dict, timestamp: datetime.datetime) -> None:
        """
        Generates the data file based on the ground truth.
        Must be implemented by concrete classes.
        
        Args:
            ground_truth (dict): Dictionary containing physics data (speed, flow).
            timestamp (datetime.datetime): The current simulation time.
        """
        pass

class IFlowStrategy(ABC):
    """
    Interface for traffic flow strategies.
    
    Enforces the Open-Closed Principle (OCP) by allowing new flow categories
    to be added without modifying existing simulator logic.
    """

    @abstractmethod
    def get_ground_truth(self, timestamp: datetime.datetime) -> dict:
        """
        Calculates the ground truth data for the specific flow level.
        
        Args:
            timestamp (datetime.datetime): The current simulation time.
            
        Returns:
            dict: The true traffic physics parameters (flow, speed).
        """
        pass