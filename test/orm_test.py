#!/usr/bin/python
# -*- coding: utf-8 -*-

import mock
import StringIO
from tornado.web import Application, RequestHandler, asynchronous
from tornado.concurrent import Future
from tornado.httpclient import HTTPRequest, HTTPResponse, HTTPClient
from tornado import gen
from tornado.testing import AsyncTestCase, AsyncHTTPClient
from tornado.testing import gen_test

from cmdb.orm_couch import Service


class TestCouchBase(AsyncTestCase):
    def setUp(self):
        super(TestCouchBase, self).setUp()  # setup io_loop
        self.couch = Service(io_loop=self.io_loop)
        self.couch.set_db('cmdb')

    @gen_test(timeout=3)
    def test_all_docs(self):
        response = yield self.couch._all_docs()
        self.assertEqual('', response)

    @gen_test(timeout=3)
    def test_has_doc(self):
        response = yield self.couch.has_doc('172.16.200.105:8080')
        self.assertEqual(200, response)

    @gen_test(timeout=10)
    def test_get_doc(self):
        pass


def setup_fetch(fetch_mock, status_code, body=None):
    def side_effect(request, **kwargs):
        if request is not HTTPRequest:
            request = HTTPRequest(request)
        print(request.url)
        buffer = StringIO.StringIO(body)
        response = HTTPResponse(request, status_code, None, buffer)
        future = Future()
        future.set_result(response)
        return future
    fetch_mock.side_effect = side_effect