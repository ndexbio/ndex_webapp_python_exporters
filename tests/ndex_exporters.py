#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ndex_webapp_python_exporters` package."""

import os
import unittest
import tempfile
import shutil

from ndex_webapp_python_exporters import ndex_exporters


class TestNDexExporters(unittest.TestCase):
    """Tests for `ndex_webapp_python_exporters` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_parse_arguments(self):
        res = ndex_exporters._parse_arguments('hi', ['graphml'])
        self.assertEqual(res.exporter, 'graphml')
        self.assertEqual(res.verbose, 1)
        self.assertEqual(res.file, None)
        self.assertEqual(res.out, None)

    def test_setuplogging(self):
        res = ndex_exporters._parse_arguments('hi', ['graphml'])
        ndex_exporters._setuplogging(res)

    def test_main_invalid_cx(self):
        temp_dir = tempfile.mkdtemp()
        try:
            invalid_cx_file = os.path.join(temp_dir, 'invalid.cx')
            out_graphml_file = os.path.join(temp_dir, 'output.graphml')
            with open(invalid_cx_file, 'w') as f:
                f.write('blah\n')
                f.flush()
            args = ['ndex_exporters.py', 'graphml',
                    '--' + ndex_exporters.FILE_FLAG,
                    invalid_cx_file,
                    '--' + ndex_exporters.OUT_FLAG,
                    out_graphml_file]
            ecode = ndex_exporters.main(args)
            self.assertEqual(ecode, 2)

        finally:
            shutil.rmtree(temp_dir)
