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
# File: parsers/sumo.py
# Author: Gabriel Moraes
# Date: 2026-08-16

from typing import List, Optional, Tuple
import xml.etree.ElementTree as ET

try:
    import pyproj
except ImportError:
    pyproj = None

from src.core.map_topology import MapTopology
from src.parsers.base import IMapParser


class SumoNetMapParser(IMapParser):
    """
    Parser for SUMO Network XML files (.net.xml, .net.xml.gz).
    Extracts road topologies, junction nodes, edge shapes, and projects Cartesian
    coordinates into geographic WGS84 latitude/longitude.
    """

    def can_parse(self, filepath: str, root_tag: Optional[str] = None, root_element: Optional[ET.Element] = None) -> bool:
        """Checks whether the file or XML root corresponds to a SUMO network payload."""
        filepath_lower = filepath.lower()
        if ".net.xml" in filepath_lower:
            return True
        if root_tag and root_tag.lower() == "net":
            return True
        if root_element is not None and root_element.find("location") is not None:
            return True
        return False

    def parse(self, filepath: str, topology: MapTopology) -> None:
        """Parses SUMO network XML data into the provided MapTopology."""
        _, root = self.open_xml_tree(filepath)
        topology.clear()

        loc = root.find("location")
        if loc is None:
            raise ValueError("Missing <location> element in SUMO .net.xml file")

        attrib = loc.attrib
        conv_parts = [float(v) for v in attrib.get("convBoundary", "0,0,1,1").split(",")]
        orig_parts = [float(v) for v in attrib.get("origBoundary", "0,0,1,1").split(",")]
        net_offset = [float(v) for v in attrib.get("netOffset", "0,0").split(",")]
        proj_param = attrib.get("projParameter", "!")

        conv_min_x, conv_min_y, conv_max_x, conv_max_y = conv_parts
        orig_min_lon, orig_min_lat, orig_max_lon, orig_max_lat = orig_parts

        topology.bounds = (orig_min_lat, orig_min_lon, orig_max_lat, orig_max_lon)

        # Coordinate projection setup
        proj_obj = None
        if pyproj and proj_param and proj_param != "!":
            try:
                proj_obj = pyproj.Proj(proj_param)
            except Exception:
                proj_obj = None

        dx = conv_max_x - conv_min_x
        dy = conv_max_y - conv_min_y
        dlon = orig_max_lon - orig_min_lon
        dlat = orig_max_lat - orig_min_lat

        def conv_xy_to_latlon(x: float, y: float) -> Tuple[float, float]:
            if proj_obj is not None:
                try:
                    px = x - net_offset[0]
                    py = y - net_offset[1]
                    lon_p, lat_p = proj_obj(px, py, inverse=True)
                    return float(lat_p), float(lon_p)
                except Exception:
                    pass
            # Proportional interpolation fallback
            norm_x = (x - conv_min_x) / dx if dx != 0 else 0.0
            norm_y = (y - conv_min_y) / dy if dy != 0 else 0.0
            lon = orig_min_lon + norm_x * dlon
            lat = orig_min_lat + norm_y * dlat
            return float(lat), float(lon)

        # Extract regular junctions as topological nodes
        for junc in root.findall("junction"):
            j_id = junc.attrib.get("id", "")
            j_type = junc.attrib.get("type", "")
            if j_id.startswith(":") or j_type == "internal":
                continue
            x = float(junc.attrib.get("x", 0.0))
            y = float(junc.attrib.get("y", 0.0))
            lat, lon = conv_xy_to_latlon(x, y)
            topology.add_node(j_id, lat, lon)

        # Extract non-internal edges and their geometry
        for edge in root.findall("edge"):
            if edge.attrib.get("function") == "internal":
                continue
            edge_id = edge.attrib.get("id", "")
            from_id = edge.attrib.get("from", "")
            to_id = edge.attrib.get("to", "")
            shape_str = edge.attrib.get("shape")

            if not shape_str:
                lane = edge.find("lane")
                if lane is not None:
                    shape_str = lane.attrib.get("shape")

            way_nodes: List[str] = []
            if shape_str:
                coords = shape_str.strip().split()
                for idx, coord in enumerate(coords):
                    parts = coord.split(",")
                    if len(parts) != 2:
                        continue
                    px, py = float(parts[0]), float(parts[1])
                    plat, plon = conv_xy_to_latlon(px, py)
                    node_id = f"{edge_id}#p{idx}"
                    topology.add_node(node_id, plat, plon)
                    way_nodes.append(node_id)
            else:
                if from_id and from_id in topology.nodes:
                    way_nodes.append(from_id)
                if to_id and to_id in topology.nodes:
                    way_nodes.append(to_id)

            if len(way_nodes) >= 2:
                topology.add_way(way_nodes)
