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
# File: parsers/factory.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import os
from typing import List, Optional
import xml.etree.ElementTree as ET

from src.parsers.base import IMapParser
from src.parsers.osm import OSMMapParser
from src.parsers.sumo import SumoNetMapParser


class MapParserFactory:
    """
    Factory and Registry for map file parsers.
    Complies with Open/Closed Principle (OCP) by enabling registration of new parsers
    without modifying existing classes.
    """

    def __init__(self) -> None:
        self._parsers: List[IMapParser] = []
        self.register_default_parsers()

    def register_default_parsers(self) -> None:
        """Registers the built-in OSM and SUMO network parsers."""
        self._parsers.clear()
        self._parsers.append(SumoNetMapParser())
        self._parsers.append(OSMMapParser())

    def register_parser(self, parser: IMapParser, prepend: bool = True) -> None:
        """Registers a custom parser strategy."""
        if prepend:
            self._parsers.insert(0, parser)
        else:
            self._parsers.append(parser)

    def get_parser(self, filepath: str) -> IMapParser:
        """
        Inspects the file and returns a matching parser strategy.
        Raises ValueError if no registered parser can handle the file.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Map file not found: '{filepath}'")

        root_tag: Optional[str] = None
        root_element: Optional[ET.Element] = None

        try:
            _, root_element = IMapParser.open_xml_tree(filepath)
            root_tag = root_element.tag
        except Exception:
            # File might be invalid XML or non-XML format
            pass

        for parser in self._parsers:
            if parser.can_parse(filepath, root_tag=root_tag, root_element=root_element):
                return parser

        raise ValueError(
            f"Unrecognized map format in '{filepath}'. "
            "Expected OpenStreetMap (.osm, .osm.gz) or SUMO Network (.net.xml, .net.xml.gz)"
        )


# Global default factory instance
default_parser_factory = MapParserFactory()
