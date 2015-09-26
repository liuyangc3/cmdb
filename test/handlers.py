#!/usr/bin/python
# -*- coding: utf-8 -*-

from mock import patch
from tornado.concurrent import Future
from tornado.testing import AsyncHTTPTestCase
from tornado.testing import gen_test

from cmdb.server import Application
from cmdb.orm_couch import CouchBase, Service


class HandlersTest(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def setUp(self):
        super(HandlersTest, self).setUp()
        self.f = Future()
        self.couch = Service()
        self.couch.set_db('cmdb')
        self.ids = r'["172.16.200.105:8080"]'

    @patch.object(CouchBase, 'list_ids')
    @gen_test(timeout=5)
    def test_root(self, mock_list_ids):
        self.f.set_result(self.ids)
        mock_list_ids.return_value = self.f
        response = yield self.http_client.fetch(self.get_url('/'))
        result = response.body.decode('string-escape').strip('"')
        self.assertEqual(self.ids, result)
