#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import unittest
from tornado.escape import json_decode
from tornado.testing import AsyncTestCase

from cmdb.orm import CouchServer


class TestCouchServer(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = 'couch_server'
        cls.server = CouchServer()

    def test_1_create(self):
        resp = self.server.create(self.database)
        self.assertEqual(resp, '{"ok":true}\n')
        # create exist database
        self.assertRaises(ValueError, self.server.create, self.database)

    def test_get_design(self):
        root = os.path.join(os.path.dirname(__file__), '../..')
        designs = self.server._get_design(root)
        file_names = [os.path.basename(name) for name in designs]
        self.assertIn('service.json', file_names)
        self.assertIn('project.json', file_names)

    def test_2_init(self):
        self.server.init(self.database)
        resp = self.server.client.fetch(
            self.server.base_url + '{0}/_design/service'.format(self.database))
        self.assertEqual(json_decode(resp.body)["_id"], "_design/service")

    def test_3_list_db(self):
        databases = self.server.list_db()
        self.assertIn(self.database, databases)

    def test_4_delete(self):
        resp = self.server.delete(self.database)
        self.assertEqual(resp, '{"ok":true}\n')
        self.assertRaises(ValueError, self.server.delete, self.database)

if __name__ == '__main__':
    unittest.main()
