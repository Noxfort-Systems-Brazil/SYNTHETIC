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
# File: core/map_provider.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from src.core.logger import logger
from src.core.map_topology import MapTopology
from src.parsers.factory import MapParserFactory, default_parser_factory
from src.services.graph_converter import GATv2GraphConverter
from src.services.spatial_service import SpatialService


class MapProvider:
    """
    Universal Map Provider acting as a pure Facade and Orchestrator.
    Coordinates map file parsing (OSM / SUMO Net), spatial geometry calculations,
    and GNN graph feature extraction while adhering strictly to SOLID principles.
    """

    def __init__(
        self,
        topology: Optional[MapTopology] = None,
        parser_factory: Optional[MapParserFactory] = None,
        spatial_service: Optional[SpatialService] = None,
        graph_converter: Optional[GATv2GraphConverter] = None,
    ) -> None:
        self.topology: MapTopology = topology if topology is not None else MapTopology()
        self.parser_factory: MapParserFactory = parser_factory if parser_factory is not None else default_parser_factory
        self.spatial_service: SpatialService = spatial_service if spatial_service is not None else SpatialService()
        self.graph_converter: GATv2GraphConverter = graph_converter if graph_converter is not None else GATv2GraphConverter()

    @property
    def nodes(self) -> Dict[str, Tuple[float, float]]:
        """Dictionary of {node_id: (lat, lon)}."""
        return self.topology.nodes

    @nodes.setter
    def nodes(self, value: Dict[str, Tuple[float, float]]) -> None:
        self.topology.nodes = value

    @property
    def ways(self) -> List[List[str]]:
        """List of node ID sequences representing road ways."""
        return self.topology.ways

    @ways.setter
    def ways(self, value: List[List[str]]) -> None:
        self.topology.ways = value

    @property
    def road_nodes(self) -> Set[str]:
        """Set of node IDs associated with navigable road ways."""
        return self.topology.road_nodes

    @road_nodes.setter
    def road_nodes(self, value: Set[str]) -> None:
        self.topology.road_nodes = value

    @property
    def bounds(self) -> Optional[Tuple[float, float, float, float]]:
        """Geographic bounds (min_lat, min_lon, max_lat, max_lon)."""
        return self.topology.bounds

    @bounds.setter
    def bounds(self, value: Optional[Tuple[float, float, float, float]]) -> None:
        self.topology.bounds = value

    @classmethod
    def load_from_file(cls, filepath: str, parser_factory: Optional[MapParserFactory] = None) -> "MapProvider":
        """
        Factory method to load and parse any supported map format (.osm, .osm.gz, .net.xml, .net.xml.gz).
        Wraps parsing exceptions with clear domain logging and error boundaries.
        """
        logger.info(f"Loading map from file: {filepath}")
        if not os.path.exists(filepath):
            logger.error(f"Map file not found at '{filepath}'")
            raise FileNotFoundError(f"Map file not found: '{filepath}'")

        provider = cls(parser_factory=parser_factory)
        try:
            provider.parse_file(filepath)
            logger.info(
                f"Successfully loaded Map ({os.path.basename(filepath)}). "
                f"Nodes: {len(provider.nodes)}, Ways: {len(provider.ways)}, "
                f"Bounds: {provider.bounds}"
            )
            return provider
        except (ET.ParseError, FileNotFoundError, PermissionError, ValueError) as e:
            logger.error(f"Failed to parse map file '{filepath}': {str(e)}")
            raise ValueError(f"Invalid map file or path: {str(e)}") from e

    def parse_file(self, filepath: str) -> None:
        """
        Delegates map parsing to the matching parser registered in the factory.
        """
        parser = self.parser_factory.get_parser(filepath)
        parser.parse(filepath, self.topology)

    def parse_osm_file(self, filepath: str) -> None:
        """Backwards-compatible wrapper for loading an OSM file."""
        self.parse_file(filepath)

    def parse_sumo_net_file(self, filepath: str) -> None:
        """Backwards-compatible wrapper for loading a SUMO network file."""
        self.parse_file(filepath)

    def get_bounds(self) -> Optional[Tuple[float, float, float, float]]:
        """Returns (min_lat, min_lon, max_lat, max_lon)."""
        return self.bounds

    def snap_to_road(self, lat: float, lon: float) -> Tuple[float, float]:
        """
        Delegates point-to-road snapping calculations to the SpatialService.
        """
        return self.spatial_service.snap_to_road(lat, lon, self.topology)

    def parse_to_graph(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Delegates graph tensor conversion to the GATv2GraphConverter.
        """
        return self.graph_converter.convert(self.topology)

    def parse_osm_to_graph(self) -> Tuple[np.ndarray, np.ndarray]:
        """Backwards-compatible alias for GATv2 context extraction."""
        return self.parse_to_graph()


# Backwards compatibility alias
OSMMapProvider = MapProvider
