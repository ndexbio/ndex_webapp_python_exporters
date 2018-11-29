#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ndex_webapp_python_exporters` package."""

import io
import unittest

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
        self.assertEqual(ge._convert_data_type('foo'), 'foo')
        self.assertEqual(ge._convert_data_type('int'), 'integer')
        self.assertEqual(ge._convert_data_type('str'), 'string')
        self.assertEqual(ge._convert_data_type('bool'), 'boolean')

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
        print(fakeout.getvalue())
        self.assertTrue(fakeout.getvalue().
                        startswith('<?xml version="1.0" '
                                   'encoding="UTF-8" standalone="no"?>'))
        self.assertTrue('<node id="1"><data key="name">AKT1</data>' in
                        fakeout.getvalue())
