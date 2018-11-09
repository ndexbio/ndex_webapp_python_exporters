#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ndex_webapp_python_exporters` package."""

import io
import json
import unittest

from ndex_webapp_python_exporters.exporters import NDexExporter
from ndex_webapp_python_exporters.exporters import GraphMLExporter


class TestExporters(unittest.TestCase):
    """Tests for `ndex_webapp_python_exporters` package."""

    def get_small_network_withsubnet(self):
        return """[{"numberVerification": [{"longNumber": 281474976710655}]},
         {"metaData": [{"idCounter": 0, "name": "nodes"}, {"idCounter": 0,
          "name": "edges"}]}, {"networkAttributes": [{"v": "Test Types", "n":
           "name"}]}, {"subNetworks": [{"nodes": [1, 2, 3], "edges": [1, 2],
            "@id": 0}]}, {"cyViews": [{"s": 0, "@id": 0}]}, {"nodes": [{"@id":
             1, "n": "Node with Types"}]}, {"nodes": [{"@id": 2, "n": "A"}]},
              {"nodes": [{"@id": 3, "n": "B"}]}, {"edges": [{"i":
               "interacts_with", "s": 1, "@id": 1, "t": 2}]}, {"edges":
                [{"i": "interacts_with", "s": 1, "@id": 2, "t": 3}]},
                 {"nodeAttributes": [{"d": "list_of_long", "v": [5, 75],
                  "po": 1, "n": "long_list"}, {"d": "integer", "v": 5, "po":
                   1, "n": "int"}, {"d": "double", "v": 2.5, "po": 1, "n":
                    "double"}, {"d": "list_of_integer", "v": [5, -20], "po":
                     1, "n": "int_list"}, {"d": "list_of_double", "v": [2.5,
                      3.7], "po": 1, "n": "double_list"}, {"d": "long", "v":
                       5, "po": 1, "n": "long"}, {"d": "list_of_string", "v":
                        ["mystring", "myotherstring"], "po": 1, "n":
                         "string_list"}, {"d": "boolean", "v": true, "po": 1,
                          "n": "bool"}, {"d": "list_of_boolean", "v": [false,
                           true], "po": 1, "n": "bool_list"}, {"v":
                            "mystring", "po": 1, "n": "string"}]},
                             {"edgeAttributes": [{"v": "interacts_with", "po":
                              1, "n": "interaction"}]}, {"edgeAttributes":
                               [{"v": "interacts_with", "po": 2, "n":
                                "interaction"}]}]"""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_NDexExporter_export_raises_exception(self):
        nd = NDexExporter()
        try:
            nd.export(None, None)
            self.fail('Expected NotImplementedError')
        except NotImplementedError as nie:
            self.assertEqual(str(nie), 'Should be implemented by subclass')

    def test_graphmlexporter_clear_internal_variables(self):
        ge = GraphMLExporter()
        self.assertEqual(ge._nodes, None)
        self.assertEqual(ge._net_attr, None)
        self.assertEqual(ge._keys_edge, None)

        ge._clear_internal_variables()
        self.assertEqual(ge._nodes, None)
        self.assertEqual(ge._net_attr, None)
        self.assertEqual(ge._keys_edge, None)

        ge._nodes = 'hi'
        ge._clear_internal_variables()
        self.assertEqual(ge._nodes, None)

    def test_graphmlexporter_split_json(self):
        ge = GraphMLExporter()
        ge._split_json(None)
        self.assertEqual(ge._nodes, None)

        data = json.loads(self.get_small_network_withsubnet())
        ge._split_json(data)
        self.assertEqual(len(ge._nodes), 3)
        self.assertEqual(len(ge._edges[0]), 4)
        self.assertEqual(ge._node_attr[0]['po'], 1)
        self.assertEqual(ge._edge_attr[0]['po'], 1)
        self.assertEqual(ge._net_attr[0]['n'], 'name')

    def test_graphmlexporter_small_network(self):
        ge = GraphMLExporter()
        fakein = io.StringIO(self.get_small_network_withsubnet())
        fakeout = io.StringIO()
        ge.export(fakein, fakeout)
        import sys
        sys.stdout.write(fakeout.getvalue())
        self.assertTrue(fakeout.getvalue().
                        startswith('<?xml version="1.0" '
                                   'encoding="UTF-8" standalone="no"?>'))
        self.assertTrue('<node id="2"><data key="name">A</data></node>' in
                        fakeout.getvalue())
