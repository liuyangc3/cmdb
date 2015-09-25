#!/usr/bin/python
# -*- coding: utf-8 -*-

import mock
import StringIO
from tornado.web import Application, RequestHandler, asynchronous
from tornado.concurrent import Future
from tornado.httpclient import HTTPRequest, HTTPResponse, HTTPClient
from tornado import gen
from tornado.testing import AsyncTestCase, AsyncHTTPTestCase, AsyncHTTPClient
from tornado.testing import gen_test

from server.orm_couch import Service
from server.handlers.cmdbHandlers import ServiceOperationHanlder


class FooHanlder(RequestHandler):
    @asynchronous
    @gen.coroutine
    def put(self, *args, **kwargs):
        result = yield self.some_gen()
        self.finish(result + "Foo!")

    def get_client(self):
        """To be able to mock away the real http client and leave the http
        client used for testing alone"""
        return AsyncHTTPClient()

    @gen.coroutine
    def some_gen(self):
        client = self.get_client()
        # client.fetch can be mocked
        response = yield client.fetch('http://something_that_will_never_resolve/')
        # now we can post-process the response
        raise gen.Return(response.body[:100])


class TestCouchBase(AsyncHTTPTestCase):
    def get_app(self):
        application = Application([
            (r'/service/(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{2,5})', FooHanlder)
        ])
        return application

    def setUp(self):
        super(TestCouchBase, self).setUp()  # setup io_loop
        self.couch = Service('http://172.16.200.51:5984', self.io_loop)
        self.couch.set_db('cmdb')

    @gen_test(timeout=10)
    def test_has_doc(self):
        response = yield self.couch.has_doc('172.16.200.105:8080')
        self.assertEqual(200, response)

    @gen_test(timeout=10)
    def test_get_doc(self):
        pass

    @gen_test(timeout=10)
    def test_add_service(self):
        with mock.patch.object(FooHanlder, 'put') as put:
            setup_fetch(put, 200, "oo")
            response = yield self.http_client.fetch(self.get_url(
                '/service/172.16.200.123:8080/fuck=me'),
                method="PUT",
                body='{"fuck":"me"}'
            )
            print response.body


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