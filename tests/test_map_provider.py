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
# File: tests/test_map_provider.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import gzip
import os
import tempfile
import unittest
import numpy as np

from src.core.map_provider import MapProvider, OSMMapProvider
from src.core.map_topology import MapTopology
from src.parsers.osm import OSMMapParser
from src.parsers.sumo import SumoNetMapParser
from src.parsers.factory import MapParserFactory
from src.services.spatial_service import SpatialService
from src.services.graph_converter import GATv2GraphConverter

SAMPLE_OSM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="test">
  <bounds minlat="-23.5150" minlon="-51.2400" maxlat="-23.5070" maxlon="-51.2330"/>
  <node id="101" lat="-23.5100" lon="-51.2380"/>
  <node id="102" lat="-23.5105" lon="-51.2360"/>
  <node id="103" lat="-23.5110" lon="-51.2340"/>
  <way id="201">
    <nd ref="101"/>
    <nd ref="102"/>
    <nd ref="103"/>
    <tag k="highway" v="primary"/>
  </way>
</osm>
"""

SAMPLE_SUMO_NET_XML = """<?xml version="1.0" encoding="UTF-8"?>
<net version="1.20" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <location netOffset="-475481.54,2600660.66" 
              convBoundary="0.00,0.00,1000.00,1000.00" 
              origBoundary="-51.240000,-23.515000,-51.233000,-23.507000" 
              projParameter="!"/>
    <junction id="j1" type="priority" x="100.00" y="200.00"/>
    <junction id="j2" type="priority" x="500.00" y="600.00"/>
    <junction id=":internal_1" type="internal" x="150.00" y="250.00"/>
    <edge id="edge_1" from="j1" to="j2" shape="100.00,200.00 300.00,400.00 500.00,600.00">
        <lane id="edge_1_0" index="0" speed="13.89" length="565.68" shape="100.00,200.00 300.00,400.00 500.00,600.00"/>
    </edge>
    <edge id=":internal_edge_1" function="internal">
        <lane id=":internal_edge_1_0" index="0" speed="5.0" length="10.0" shape="150.00,250.00 160.00,260.00"/>
    </edge>
</net>
"""


class TestMapProvider(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_osm_file(self):
        osm_path = os.path.join(self.temp_dir.name, "city.osm")
        with open(osm_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_OSM_XML)

        provider = MapProvider.load_from_file(osm_path)
        self.assertIsNotNone(provider.bounds)
        self.assertAlmostEqual(provider.bounds[0], -23.5150)
        self.assertAlmostEqual(provider.bounds[1], -51.2400)
        self.assertAlmostEqual(provider.bounds[2], -23.5070)
        self.assertAlmostEqual(provider.bounds[3], -51.2330)

        self.assertEqual(len(provider.nodes), 3)
        self.assertEqual(len(provider.ways), 1)
        self.assertEqual(len(provider.road_nodes), 3)

    def test_parse_osm_gz_file(self):
        osm_gz_path = os.path.join(self.temp_dir.name, "city.osm.gz")
        with gzip.open(osm_gz_path, "wt", encoding="utf-8") as f:
            f.write(SAMPLE_OSM_XML)

        provider = OSMMapProvider.load_from_file(osm_gz_path)
        self.assertEqual(len(provider.nodes), 3)
        self.assertEqual(len(provider.ways), 1)

    def test_parse_sumo_net_file(self):
        net_path = os.path.join(self.temp_dir.name, "network.net.xml")
        with open(net_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_SUMO_NET_XML)

        provider = MapProvider.load_from_file(net_path)
        self.assertIsNotNone(provider.bounds)
        self.assertAlmostEqual(provider.bounds[0], -23.515000)
        self.assertAlmostEqual(provider.bounds[1], -51.240000)
        self.assertAlmostEqual(provider.bounds[2], -23.507000)
        self.assertAlmostEqual(provider.bounds[3], -51.233000)

        # Non-internal junctions + intermediate shape nodes
        self.assertIn("j1", provider.nodes)
        self.assertIn("j2", provider.nodes)
        self.assertIn("edge_1#p1", provider.nodes)
        self.assertEqual(len(provider.ways), 1)

    def test_parse_sumo_net_gz_file(self):
        net_gz_path = os.path.join(self.temp_dir.name, "network.net.xml.gz")
        with gzip.open(net_gz_path, "wt", encoding="utf-8") as f:
            f.write(SAMPLE_SUMO_NET_XML)

        provider = MapProvider.load_from_file(net_gz_path)
        self.assertIsNotNone(provider.bounds)
        self.assertGreater(len(provider.nodes), 0)
        self.assertGreater(len(provider.ways), 0)

    def test_snap_to_road(self):
        net_path = os.path.join(self.temp_dir.name, "test.net.xml")
        with open(net_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_SUMO_NET_XML)

        provider = MapProvider.load_from_file(net_path)
        raw_lat, raw_lon = -23.5100, -51.2360
        snapped_lat, snapped_lon = provider.snap_to_road(raw_lat, raw_lon)

        self.assertIsInstance(snapped_lat, float)
        self.assertIsInstance(snapped_lon, float)
        self.assertGreaterEqual(snapped_lat, provider.bounds[0])
        self.assertLessEqual(snapped_lat, provider.bounds[2])

    def test_parse_to_graph(self):
        net_path = os.path.join(self.temp_dir.name, "test.net.xml")
        with open(net_path, "w", encoding="utf-8") as f:
            f.write(SAMPLE_SUMO_NET_XML)

        provider = MapProvider.load_from_file(net_path)
        node_features, edge_index = provider.parse_to_graph()

        self.assertIsInstance(node_features, np.ndarray)
        self.assertIsInstance(edge_index, np.ndarray)
        self.assertEqual(node_features.shape[1], 2)
        self.assertEqual(edge_index.shape[0], 2)

    def test_invalid_file(self):
        invalid_path = os.path.join(self.temp_dir.name, "invalid.txt")
        with open(invalid_path, "w", encoding="utf-8") as f:
            f.write("Not an XML file")

        with self.assertRaises(ValueError):
            MapProvider.load_from_file(invalid_path)


class TestDecoupledComponents(unittest.TestCase):
    """Direct isolated unit tests for individual SOLID components."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_map_topology_crud(self):
        topology = MapTopology()
        self.assertTrue(topology.is_empty())

        topology.add_node("n1", -23.5, -51.2)
        topology.add_node("n2", -23.6, -51.3)
        topology.add_way(["n1", "n2"])

        self.assertFalse(topology.is_empty())
        self.assertEqual(len(topology.nodes), 2)
        self.assertEqual(len(topology.ways), 1)
        self.assertEqual(len(topology.road_nodes), 2)

        topology.update_bounds_from_nodes()
        self.assertEqual(topology.bounds, (-23.6, -51.3, -23.5, -51.2))

        topology.clear()
        self.assertTrue(topology.is_empty())
        self.assertIsNone(topology.bounds)

    def test_spatial_service_snapping(self):
        topology = MapTopology()
        topology.add_node("n1", 0.0, 0.0)
        topology.add_node("n2", 0.0, 1.0)
        topology.add_way(["n1", "n2"])

        # Test point slightly above the horizontal segment
        snapped_lat, snapped_lon = SpatialService.snap_to_road(0.1, 0.5, topology)
        self.assertAlmostEqual(snapped_lat, 0.0, places=4)
        self.assertAlmostEqual(snapped_lon, 0.5, places=4)

    def test_graph_converter(self):
        topology = MapTopology()
        topology.add_node("n1", 10.0, 20.0)
        topology.add_node("n2", 30.0, 40.0)
        topology.add_way(["n1", "n2"])

        node_features, edge_index = GATv2GraphConverter.convert(topology)
        self.assertEqual(node_features.shape, (2, 2))
        self.assertEqual(edge_index.shape, (2, 2))

    def test_parser_factory_registration(self):
        factory = MapParserFactory()
        osm_parser = OSMMapParser()
        self.assertTrue(osm_parser.can_parse("sample.osm"))
        self.assertFalse(osm_parser.can_parse("sample.unknown"))

        sumo_parser = SumoNetMapParser()
        self.assertTrue(sumo_parser.can_parse("sample.net.xml"))
        self.assertFalse(sumo_parser.can_parse("sample.osm"))


if __name__ == "__main__":
    unittest.main()
