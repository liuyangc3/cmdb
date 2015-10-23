#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from tornado.escape import json_decode
from tornado.testing import AsyncTestCase

from cmdb.orm import CouchServer, CouchBase


class TestCouchServer(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = 'couch_test'
        cls.server = CouchServer()

    def test_1_create(self):
        self.server.create(self.database)
        self.assertRaises(ValueError, self.server.create, self.database)

    def test_2_list(self):
        databases = self.server.list()
        self.assertIn(self.database, databases)

    def test_3_use(self):
        couch = self.server.use(self.database)
        self.assertIsInstance(couch, CouchBase)

    def test_4_delete(self):
        resp = self.server.delete(self.database)
        self.assertEqual(resp, '{"ok":true}\n')
        self.assertRaises(ValueError, self.server.delete, self.database)