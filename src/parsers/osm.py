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
# File: parsers/osm.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import xml.etree.ElementTree as ET
from typing import Optional

from src.core.map_topology import MapTopology
from src.parsers.base import IMapParser


class OSMMapParser(IMapParser):
    """
    Parser for OpenStreetMap (.osm, .osm.gz) XML files.
    Extracts road networks (ways with 'highway' tags), nodes, and geographical bounding boxes.
    """

    def can_parse(self, filepath: str, root_tag: Optional[str] = None, root_element: Optional[ET.Element] = None) -> bool:
        """Checks whether the file or XML root corresponds to an OpenStreetMap payload."""
        filepath_lower = filepath.lower()
        if ".osm" in filepath_lower:
            return True
        if root_tag and root_tag.lower() == "osm":
            return True
        if root_element is not None and root_element.find("node") is not None and root_element.find("location") is None:
            return True
        return False

    def parse(self, filepath: str, topology: MapTopology) -> None:
        """Parses OSM XML data into the provided MapTopology."""
        _, root = self.open_xml_tree(filepath)
        topology.clear()

        # Extract explicit bounds if present
        bounds_tag = root.find("bounds")
        if bounds_tag is not None:
            topology.bounds = (
                float(bounds_tag.attrib["minlat"]),
                float(bounds_tag.attrib["minlon"]),
                float(bounds_tag.attrib["maxlat"]),
                float(bounds_tag.attrib["maxlon"]),
            )

        min_lat, min_lon = float("inf"), float("inf")
        max_lat, max_lon = float("-inf"), float("-inf")

        # Parse all nodes
        for node in root.findall("node"):
            node_id = node.attrib["id"]
            lat = float(node.attrib["lat"])
            lon = float(node.attrib["lon"])
            topology.add_node(node_id, lat, lon)

            if topology.bounds is None:
                min_lat = min(min_lat, lat)
                min_lon = min(min_lon, lon)
                max_lat = max(max_lat, lat)
                max_lon = max(max_lon, lon)

        # Fallback bounds calculation if not defined in metadata
        if topology.bounds is None and topology.nodes:
            topology.bounds = (min_lat, min_lon, max_lat, max_lon)

        # Parse road ways with 'highway' tag
        for way in root.findall("way"):
            is_highway = False
            for tag in way.findall("tag"):
                if tag.attrib.get("k") == "highway":
                    is_highway = True
                    break

            if is_highway:
                way_nodes = [nd.attrib["ref"] for nd in way.findall("nd")]
                topology.add_way(way_nodes)
