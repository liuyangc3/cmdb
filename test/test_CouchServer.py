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
        self.server.create(self.database)
        self.assertRaises(ValueError, self.server.create, self.database)

    def test_2_list(self):
        databases = self.server.list()
        self.assertIn(self.database, databases)

    def test_4_delete(self):
        resp = self.server.delete(self.database)
        self.assertEqual(resp, '{"ok":true}\n')
        self.assertRaises(ValueError, self.server.delete, self.database)

if __name__ == '__main__':
    unittest.main()
