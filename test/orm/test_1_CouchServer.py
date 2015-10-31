#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import unittest
from tornado.escape import json_decode
from tornado.testing import AsyncTestCase, gen_test

from cmdb.orm import CouchServer


class TestCouchServer(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = 'couch_server'

    def setUp(self):
        super(TestCouchServer, self).setUp()  # io_loop
        self.server = CouchServer('http://172.16.200.51:5984', io_loop=self.io_loop)

    @gen_test(timeout=5)
    def test_1_create(self):
        resp = yield self.server.create(self.database)
        self.assertEqual(resp, '{"ok":true}\n')
        # create exist database
        # this test will cause a uncatched exception errno 10054
        # when create couchdb on a windows servier
        try:
            yield self.server.create(self.database)
        except ValueError as e:
            self.assertEqual(e.message, 'Database: {0} Exist'.format(self.database))

    def test_get_design(self):
        root = os.path.join(os.path.dirname(__file__), '../..')
        designs = self.server._get_design(root)
        file_names = [os.path.basename(name) for name in designs]
        self.assertIn('service.json', file_names)
        self.assertIn('project.json', file_names)

    @gen_test(timeout=5)
    def test_2_init(self):
        yield self.server.init(self.database)
        # check
        resp = yield self.server.client.fetch('{0}/_design/service'.format(self.database))
        self.assertEqual(json_decode(resp.body)["_id"], "_design/service")

    @gen_test(timeout=5)
    def test_3_list_db(self):
        databases = yield self.server.list_db()
        self.assertIn(self.database, databases)

    @gen_test(timeout=3)
    def test_4_delete(self):
        resp = yield self.server.delete(self.database)
        self.assertEqual(resp, '{"ok":true}\n')
        try:
            yield self.server.delete(self.database)
        except ValueError as e:
            self.assertEqual(e.message, 'Database: {0} not Exist'.format(self.database))

if __name__ == '__main__':
    unittest.main()
