#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
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

    def test_2_list(self):
        databases = self.server.list()
        self.assertIn(self.database, databases)

    def test_3_fetch(self):
        resp = self.server.fetch('_all_dbs')
        self.assertEqual(resp.code, 200)
        resp = self.server.fetch('couch-test', method="PUT", body='')
        self.assertEqual(resp.body, '{"ok":true}\n')
        resp = self.server.fetch('couch-test', method="DELETE")
        self.assertEqual(resp.body, '{"ok":true}\n')

    def test_4_delete(self):
        resp = self.server.delete(self.database)
        self.assertEqual(resp, '{"ok":true}\n')
        self.assertRaises(ValueError, self.server.delete, self.database)

if __name__ == '__main__':
    unittest.main()
