#!/usr/bin/python
# -*- coding: utf-8 -*-

from mock import patch
from tornado import gen
from tornado.httpclient import HTTPRequest
from tornado.escape import json_encode
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
        self.service_id = '172.16.200.999:8080'
        self.service_id_not_default_port = '172.16.200.999:9090'
        self.ids = r'["172.16.200.105:8080"]'

    @patch.object(CouchBase, 'list_ids')
    @gen_test(timeout=5)
    def test_root(self, mock_list_ids):
        self.f.set_result(self.ids)
        mock_list_ids.return_value = self.f
        response = yield self.http_client.fetch(self.get_url('/'))
        self.assertEqual(self.ids, response.body.decode('string-escape').strip('"'))

    @gen_test(timeout=3)
    def test_service_get(self):
        """ GET /service/service_id """
        response = yield self.http_client.fetch(
            self.get_url('/service/{0}'.format(self.service_id)),
            method="GET"
        )
        self.assertEqual('', response.body)

    @gen_test(timeout=5)
    def test_service_post(self):
        """ POST /service/service_id """
        print(self.get_url('/service/{0}'.format(self.service_id)))
        req = HTTPRequest(
            self.get_url('/service/{0}'.format(self.service_id)),
            method="POST",
            body=json_encode({"test": 123})
        )
        response = yield self.http_client.fetch(req)
        self.assertEqual('', response.body)

    @gen_test(timeout=5)
    def test_service_put(self):
        """ PUT /service/service_id """
        response = yield self.http_client.fetch(
            self.get_url('/service/172.16.200.211:8080'),
            method="PUT"
        )

    @gen_test(timeout=5)
    def test_service_delete(self):
        """ DELETE /service/service_id """
        response = yield self.http_client.fetch(
            self.get_url('/service/172.16.200.211:8080'),
            method="DELETE"
        )