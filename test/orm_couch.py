#!/usr/bin/python
# -*- coding: utf-8 -*-

import mock
from tornado.concurrent import Future
from tornado.escape import json_decode
from tornado.httpclient import HTTPRequest, HTTPResponse
from tornado.testing import AsyncTestCase
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
        r = json_decode(response)
        self.assertIsInstance(r, dict)

    @gen_test(timeout=3)
    def test_list_ids(self):
        response = yield self.couch.list_ids()
        self.assertIsInstance(response, list)

    @gen_test(timeout=3)
    def test_get_doc(self):
        response = yield self.couch.get_doc('172.16.200.211:8080')
        r = json_decode(response)
        self.assertIsInstance(r, dict)

    @gen_test(timeout=3)
    def test_has_doc(self):
        response = yield self.couch.has_doc('172.16.200.211:8080')
        self.assertEqual(True, response)

    @gen_test(timeout=3)
    def test_del_doc(self):
        response = yield self.couch.del_doc('172.16.200.211:8080')
        self.assertEqual(True, response)

    @gen_test(timeout=3)
    def test_get_doc_rev(self):
        response = yield self.couch.get_doc_rev('172.16.200.211:8080')
        self.assertEqual('', response)


class TestService(AsyncTestCase):
    def setUp(self):
        super(TestService, self).setUp()  # setup io_loop
        self.couch = Service(io_loop=self.io_loop)
        self.couch.set_db('cmdb')

    @gen_test(timeout=3)
    def test_save_service(self):
        response = yield self.couch.save_service('172.16.200.211:8080', x=1)
        r = json_decode(response)
        self.assertEqual(True, r["ok"])


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