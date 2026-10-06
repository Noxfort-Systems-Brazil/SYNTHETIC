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
# File: parsers/base.py
# Author: Gabriel Moraes
# Date: 2026-08-16

from abc import ABC, abstractmethod
import gzip
import os
import xml.etree.ElementTree as ET
from typing import Optional, Tuple

from src.core.map_topology import MapTopology


class IMapParser(ABC):
    """
    Abstract interface for map format parsers.
    Follows Single Responsibility and Open/Closed principles, allowing new map formats
    (e.g., GeoJSON, Lanelet2, OpenDRIVE) to be integrated without altering core logic.
    """

    @abstractmethod
    def can_parse(self, filepath: str, root_tag: Optional[str] = None, root_element: Optional[ET.Element] = None) -> bool:
        """
        Determines whether this parser can handle the given map file or root XML element.
        """
        pass

    @abstractmethod
    def parse(self, filepath: str, topology: MapTopology) -> None:
        """
        Parses the map file and populates the provided MapTopology object.
        """
        pass

    @staticmethod
    def open_xml_tree(filepath: str) -> Tuple[ET.ElementTree, ET.Element]:
        """
        Opens an XML file handling transparent gzip decompression and returns (tree, root).
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Map file not found: '{filepath}'")

        is_gzip = filepath.endswith(".gz")
        if not is_gzip:
            try:
                with open(filepath, "rb") as f_test:
                    magic = f_test.read(2)
                    if magic == b"\x1f\x8b":
                        is_gzip = True
            except Exception:
                pass

        if is_gzip:
            with gzip.open(filepath, "rb") as f:
                tree = ET.parse(f)
        else:
            tree = ET.parse(filepath)

        root = tree.getroot()
        return tree, root
