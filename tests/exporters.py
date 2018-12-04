#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ndex_webapp_python_exporters` package."""

import io
import unittest
import networkx as nx

from ndex_webapp_python_exporters.exporters import NDexExporter
from ndex_webapp_python_exporters.exporters import GraphMLExporter
from ndex_webapp_python_exporters import exporters


class TestExporters(unittest.TestCase):
    """Tests for `ndex_webapp_python_exporters` package."""

    def get_small_network_withsubnet(self):
        return """[{"numberVerification": [{"longNumber": 281474976710655}]},
         {"metaData": [{"consistencyGroup": 1, "elementCount": 1,
          "lastUpdate": 1493670999647, "name": "ndexStatus", "properties":
           [], "version": "1.0"}, {"consistencyGroup": 1, "elementCount": 1,
            "lastUpdate": 1493670999655, "name": "provenanceHistory",
             "properties": [], "version": "1.0"}, {"consistencyGroup": 1,
              "elementCount": 1, "lastUpdate": 1492530173.8275478, "name":
               "@context", "properties": [], "version": "1.0"},
                {"consistencyGroup": 1, "elementCount": 6, "lastUpdate":
                 1492530173.827551, "name": "networkAttributes",
                  "properties": [], "version": "1.0"}, {"consistencyGroup":
                   1, "elementCount": 2, "idCounter": 2, "lastUpdate":
                    1492530173.827552, "name": "nodes", "properties":
                     [], "version": "1.0"}, {"consistencyGroup": 1,
                      "elementCount": 6, "lastUpdate": 1492530173.827553,
                       "name": "nodeAttributes", "properties": [],
                        "version": "1.0"}, {"consistencyGroup": 1,
                         "elementCount": 1, "idCounter": 1, "lastUpdate":
                          1492530173.827553, "name": "edges", "properties":
                           [], "version": "1.0"}, {"consistencyGroup": 1,
                            "elementCount": 5, "lastUpdate": 1492530173.827554,
                             "name": "edgeAttributes", "properties": [],
                              "version": "1.0"}]}, {"ndexStatus":
                               [{"externalId": "aef60609-244d-11e7-8f50-0ac135e8bacf",
                                "creationTime": 1492530172454, "modificationTime":
                                 1493670999647, "visibility": "PRIVATE",
                                  "published": false, "nodeCount": 2,
                                   "edgeCount": 1, "owner": "drh", "ndexServerURI":
                                    "http://public.ndexbio.org", "readOnly": false}]},
                                     {"@context": [{"HGNC":
                                      "http://resources.openbel.org/belframework/20150611/namespace/hgnc-human-genes.belns",
                                       "CHEBI": "http://resources.openbel.org/belframework/20150611/namespace/chebi.belns"}]},
                                        {"networkAttributes": [{"n": "name", "v": "GPCR Test Document 1"}, {"n": "description",
                                         "v": "hello"}, {"n": "version", "v": "0.1"}, {"n": "authors", "v": "Dexter"},
                                          {"n": "contact", "v": "NA"}, {"n": "ndex:sourceFormat", "v": "PyBEL"}]},
                                           {"nodes": [{"@id": 0, "n": "GNAS"}, {"@id": 1, "n": "AKT1"}]},
                                            {"nodeAttributes": [{"po": 0, "n": "function", "v": "Protein"},
                                             {"po": 0, "n": "namespace", "v": "HGNC"}, {"po": 0, "n":
                                              "identifier", "v": "GNAS"}, {"po": 1, "n": "function",
                                               "v": "Protein"}, {"po": 1, "n": "namespace", "v": "HGNC"},
                                                {"po": 1, "n": "identifier", "v": "AKT1"}]}, {"edges":
                                                [{"@id": 0, "s": 0, "t": 1, "i": "decreases"}]},
                                                {"edgeAttributes": [{"po": 0, "n": "evidence", "v": "blah"},
                                                 {"po": 0, "n": "citation_type", "v": "PubMed"},
                                                 {"po": 0, "n": "citation_name", "v": "Inact"},
                                                  {"po": 0, "n": "citation_reference", "v": "25961504"},
                                                   {"po": 0, "n": "PERTURBATION_METHOD", "v": "Cre-Lox Knockout"}]},
                                                   {"status": [{"error": "", "success": true}]}]""" # noqa

    def get_four_node_network(self):
        return """[{"numberVerification":[{"longNumber":281474976710655}]},
        {"metaData":[{"consistencyGroup":1,"elementCount":1,
        "lastUpdate":1507591862060,"name":"ndexStatus","properties":[],
        "version":"1.0"},{"consistencyGroup":1,"elementCount":1,"lastUpdate":1507136211530,
        "name":"provenanceHistory","properties":[],"version":"1.0"},{"consistencyGroup":1,
        "elementCount":4,"idCounter":4,"name":"nodes","properties":[],"version":"1.0"},
        {"consistencyGroup":1,"elementCount":5,"idCounter":14,"name":"edges","properties":[],
        "version":"1.0"},{"consistencyGroup":1,"elementCount":5,"name":"edgeAttributes",
        "properties":[],"version":"1.0"}]},{"ndexStatus":[{"externalId":"a0e1b00c-933e-11e7-bcce-06832d634f41",
        "creationTime":1504728285450,"modificationTime":1507591862060,"visibility":"PUBLIC",
        "published":false,"nodeCount":4,"edgeCount":5,"owner":"scratch",
        "ndexServerURI":"http://dev.ndexbio.org","readOnly":true}]},
         {"provenanceHistory":[{"entity":{"uri":null,"creationEvent":null,"properties":[]}}]}, {"nodes":[{
  "@id" : 1,
  "n" : "A"
}, {
  "@id" : 2,
  "n" : "B"
}, {
  "@id" : 3,
  "n" : "C"
}, {
  "@id" : 4,
  "n" : "D"
}]}, {"edges":[{
  "@id" : 10,
  "s" : 1,
  "t" : 2
}, {
  "@id" : 11,
  "s" : 1,
  "t" : 3
}, {
  "@id" : 12,
  "s" : 1,
  "t" : 4
}, {
  "@id" : 13,
  "s" : 2,
  "t" : 3
}, {
  "@id" : 14,
  "s" : 2,
  "t" : 4
}]}, 
{"nodeAttributes":[{
  "po" : 1,
  "n" : "mynode",
  "v" : "hello",
  "d" : "str"}
]},
{"edgeAttributes":[{
  "po" : 10,
  "n" : "weight",
  "v" : "1.234",
  "d" : "double"
}, {
  "po" : 11,
  "n" : "weight",
  "v" : "2.554",
  "d" : "double"
}, {
  "po" : 12,
  "n" : "weight",
  "v" : "5.789",
  "d" : "double"
}, {
  "po" : 13,
  "n" : "weight",
  "v" : "2.011",
  "d" : "double"
}, {
  "po" : 14,
  "n" : "weight",
  "v" : "7.788",
  "d" : "double"
}, {
  "po" : 10,
  "n" : "somedata",
  "v" : "['hi','bye']",
  "d" : "list"
}, {
  "po" : 10,
  "n" : "haha",
  "v" : "yoyo",
  "d" : "list_of_string"
}]},{"status":[{"error":"","success":true}]}]""" # noqa

    def get_sixnode_eightedge(self):
        return """[{"numberVerification":[{"longNumber":281474976710655}]},{"metaData":[{"name":"provenanceHistory","elementCount":1,"version":"1.0","consistencyGroup":1,"properties":[]},{"name":"nodes","elementCount":6,"idCounter":92,"version":"1.0","consistencyGroup":1,"properties":[]},{"name":"edges","elementCount":8,"idCounter":93,"version":"1.0","consistencyGroup":1,"properties":[]},{"name":"networkAttributes","elementCount":3,"version":"1.0","consistencyGroup":1,"properties":[]},{"name":"edgeAttributes","elementCount":16,"version":"1.0","consistencyGroup":1,"properties":[]},{"name":"cartesianLayout","elementCount":6,"version":"1.0","consistencyGroup":1,"properties":[]},{"name":"cyVisualProperties","elementCount":3,"version":"1.0","consistencyGroup":1,"properties":[]}]},
{"provenanceHistory":[{"entity":{"properties":[],"uri":null,"creationEvent":{"properties":[{"name":"cyNDEx2 Version","value":"2.3.0"},{"name":"Cytoscape Version","value":"3.7.0"},{"name":"dc:title","value":"Query example net"}],"eventType":"CyNDEx-2 Upload","startedAtTime":1543611130591,"endedAtTime":1543611130591,"inputs":null}}}]},
 {"nodes":[{"@id":74,"n":"F"}, {"@id":72,"n":"E"}, {"@id":70,"n":"D"}, {"@id":68,"n":"C"}, {"@id":66,"n":"B"}, {"@id":64,"n":"A"}]},
 {"edges":[{"@id":82,"s":72,"t":66,"i":"interacts with"}, {"@id":84,"s":70,"t":68,"i":"interacts with"}, {"@id":86,"s":68,"t":74,"i":"interacts with"}, {"@id":90,"s":66,"t":68,"i":"interacts with"}, {"@id":88,"s":66,"t":74,"i":"interacts with"}, {"@id":80,"s":64,"t":74,"i":"interacts with"}, {"@id":78,"s":64,"t":68,"i":"interacts with"}, {"@id":76,"s":64,"t":66,"i":"interacts with"}]},
 {"networkAttributes":[{"n":"name","v":"Query example net"}, {"n":"description","v":"used to determine if the query works as expected"}, {"n":"version","v":"1"}]},
 {"edgeAttributes":[{"po":82,"n":"name","v":"E (interacts with) B"}, {"po":82,"n":"interaction","v":"interacts with"}, {"po":84,"n":"name","v":"D (interacts with) C"}, {"po":84,"n":"interaction","v":"interacts with"}, {"po":86,"n":"name","v":"C (interacts with) F"}, {"po":86,"n":"interaction","v":"interacts with"}, {"po":90,"n":"name","v":"B (interacts with) C"}, {"po":90,"n":"interaction","v":"interacts with"}, {"po":88,"n":"name","v":"B (interacts with) F"}, {"po":88,"n":"interaction","v":"interacts with"}, {"po":80,"n":"name","v":"A (interacts with) F"}, {"po":80,"n":"interaction","v":"interacts with"}, {"po":78,"n":"name","v":"A (interacts with) C"}, {"po":78,"n":"interaction","v":"interacts with"}, {"po":76,"n":"name","v":"A (interacts with) B"}, {"po":76,"n":"interaction","v":"interacts with"}]},
 {"cartesianLayout":[{"node":74,"x":-362.0,"y":49.0}, {"node":72,"x":-10.0,"y":130.0}, {"node":70,"x":122.0,"y":-56.0}, {"node":68,"x":-27.0,"y":-126.0}, {"node":66,"x":-140.0,"y":44.0}, {"node":64,"x":-264.0,"y":-125.0}]},{"status":[{"error":"","success":true}]}]""" # noqa

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

    def test_graphmlexporter_convert_data_type(self):
        ge = GraphMLExporter()
        self.assertEqual(ge._convert_data_type('foo'), 'string')
        self.assertEqual(ge._convert_data_type('int'), 'int')
        self.assertEqual(ge._convert_data_type('str'), 'string')
        self.assertEqual(ge._convert_data_type('bool'), 'boolean')
        self.assertEqual(ge._convert_data_type('float'), 'float')
        self.assertEqual(ge._convert_data_type('list'), 'string')
        self.assertEqual(ge._convert_data_type('list_of_string'), 'string')
        self.assertEqual(ge._convert_data_type('boolean'), 'boolean')
        self.assertEqual(ge._convert_data_type('double'), 'double')
        self.assertEqual(ge._convert_data_type('integer'), 'int')
        self.assertEqual(ge._convert_data_type('long'), 'long')
        self.assertEqual(ge._convert_data_type('string'), 'string')
        self.assertEqual(ge._convert_data_type('list_of_boolean'), 'string')
        self.assertEqual(ge._convert_data_type('list_of_double'), 'string')
        self.assertEqual(ge._convert_data_type('list_of_integer'), 'string')
        self.assertEqual(ge._convert_data_type('list_of_long'), 'string')
        self.assertEqual(ge._convert_data_type('list_of_string'), 'string')

    def test_graphmlexporter_translate_edge_key(self):
        ge = GraphMLExporter()
        self.assertEqual(ge._translate_edge_key_names('foo'), 'foo')
        self.assertEqual(ge._translate_edge_key_names('i'), 'interaction')
        self.assertEqual(ge._translate_edge_key_names(exporters.AT_ID_KEY),
                         'key')

    def test_graphmlexporter_translate_node_key_names(self):
        ge = GraphMLExporter()
        self.assertEqual(ge._translate_node_key_names('blah'), 'blah')
        self.assertEqual(ge._translate_node_key_names(exporters.N_KEY),
                         'name')
        self.assertEqual(ge._translate_node_key_names(exporters.R_KEY),
                         'represents')

    def test_graphmlexporter_clear_internal_variables(self):
        ge = GraphMLExporter()
        self.assertEqual(ge._cxnetwork, None)

        ge._clear_internal_variables()
        self.assertEqual(ge._cxnetwork, None)

        ge._cxnetwork = 'hi'
        ge._clear_internal_variables()
        self.assertEqual(ge._cxnetwork, None)

    def test_graphmlexporter_small_network(self):

        ge = GraphMLExporter()
        fakein = io.StringIO(self.get_small_network_withsubnet())
        fakeout = io.StringIO()

        ge.export(fakein, fakeout)
        self.assertTrue(fakeout.getvalue().
                        startswith('<?xml version="1.0" '
                                   'encoding="UTF-8" standalone="no"?>'))
        self.assertTrue('<node id="1"><data key="name">AKT1</data>' in
                        fakeout.getvalue())

        graph = nx.readwrite.graphml.parse_graphml(fakeout.getvalue())
        self.assertEqual(len(graph.nodes()), 2)
        self.assertTrue('0' in graph.nodes())
        self.assertTrue('1' in graph.nodes())
        self.assertEqual(graph.edges(), [('0', '1')])
        self.assertEqual(str(graph.graph['name']), 'GPCR Test Document 1')
        self.assertEqual(str(graph.graph['description']), 'hello')
        self.assertEqual(str(graph.graph['version']), '0.1')
        self.assertEqual(str(graph.graph['authors']), 'Dexter')
        self.assertEqual(str(graph.graph['contact']), 'NA')
        self.assertEqual(str(graph.graph['ndex:sourceFormat']), 'PyBEL')

        self.assertEqual(graph.node['0']['name'], 'GNAS')
        self.assertEqual(graph.node['0']['function'], 'Protein')
        self.assertEqual(graph.node['0']['namespace'], 'HGNC')

        self.assertEqual(graph.node['1']['name'], 'AKT1')
        self.assertEqual(graph.node['1']['function'], 'Protein')
        self.assertEqual(graph.node['1']['namespace'], 'HGNC')

        self.assertEqual(graph.edge['0']['1']['interaction'], 'decreases')
        self.assertEqual(graph.edge['0']['1']['evidence'], 'blah')
        self.assertEqual(graph.edge['0']['1']['citation_type'], 'PubMed')
        self.assertEqual(graph.edge['0']['1']['citation_name'], 'Inact')
        self.assertEqual(graph.edge['0']['1']['citation_reference'],
                         '25961504')
        self.assertEqual(graph.edge['0']['1']['PERTURBATION_METHOD'],
                         'Cre-Lox Knockout')

    def test_four_node_network_graphml_exporter(self):
        ge = GraphMLExporter()
        fakein = io.StringIO(self.get_four_node_network())
        fakeout = io.StringIO()

        ge.export(fakein, fakeout)

        graph = nx.readwrite.graphml.parse_graphml(fakeout.getvalue())
        self.assertEqual(len(graph.nodes()), 4)
        self.assertTrue('1' in graph.nodes())
        self.assertTrue('2' in graph.nodes())
        self.assertTrue('3' in graph.nodes())
        self.assertTrue('4' in graph.nodes())

        self.assertEqual(len(graph.edges()), 5)
        self.assertTrue(('1', '2') in graph.edges())
        self.assertTrue(('1', '3') in graph.edges())
        self.assertTrue(('1', '4') in graph.edges())
        self.assertTrue(('2', '3') in graph.edges())
        self.assertTrue(('2', '4') in graph.edges())

        # the type was set to list so it was converted to string
        self.assertEqual(graph.edge['1']['2']['somedata'], "['hi','bye']")
        # the type was set to list_of_string so it was converted to string
        self.assertEqual(graph.edge['1']['2']['haha'], 'yoyo')

        self.assertEqual(graph.edge['1']['2']['weight'], 1.234)
        self.assertEqual(graph.edge['1']['3']['weight'], 2.554)
        self.assertEqual(graph.edge['1']['4']['weight'], 5.789)
        self.assertEqual(graph.edge['2']['3']['weight'], 2.011)
        self.assertEqual(graph.edge['2']['4']['weight'], 7.788)

    def test_six_node_eight_edge_network_graphml_exporter(self):
        ge = GraphMLExporter()

        fakein = io.StringIO(self.get_sixnode_eightedge())
        fakeout = io.StringIO()

        ge.export(fakein, fakeout)

        graph = nx.readwrite.graphml.parse_graphml(fakeout.getvalue())
        self.assertEqual(len(graph.nodes()), 6)
        self.assertTrue('64' in graph.nodes())
        self.assertTrue('66' in graph.nodes())
        self.assertTrue('68' in graph.nodes())
        self.assertTrue('70' in graph.nodes())
        self.assertTrue('72' in graph.nodes())
        self.assertTrue('74' in graph.nodes())

        self.assertEqual(len(graph.edges()), 8)
        self.assertTrue(('72', '66') in graph.edges())
        self.assertTrue(('70', '68') in graph.edges())
        self.assertTrue(('68', '74') in graph.edges())
        self.assertTrue(('66', '68') in graph.edges())
        self.assertTrue(('66', '74') in graph.edges())
        self.assertTrue(('64', '74') in graph.edges())
        self.assertTrue(('64', '68') in graph.edges())
        self.assertTrue(('64', '66') in graph.edges())

        self.assertEqual(graph.edge['72']['66']['name'],
                         'E (interacts with) B')
