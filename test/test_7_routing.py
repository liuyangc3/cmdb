#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import mock
from tornado.web import StaticFileHandler
from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.testing import gen_test
from tornado.testing import AsyncHTTPTestCase

from cmdb import handlers


class RoutingTestCase(AsyncHTTPTestCase):
    def get_app(self):
        from cmdb.route import router
        return Application(router, {"debug": True})

    def get_new_ioloop(self):
        # AsyncHTTPTestCase creates its own local IOLoop
        # any test case function should use it
        # https://github.com/tornadoweb/tornado/issues/663
        return IOLoop.instance()

    def setUp(self):
        super(RoutingTestCase, self).setUp()
        self.prefix = '/api/v1'

    def test_routing_index(self):
        with mock.patch.object(handlers.IndexHandler, 'get') as m:
            m.return_value = None
            self.fetch('/')
            m.assert_called_once_with()

    def test_routing_static(self):
        with mock.patch.object(StaticFileHandler, 'get') as m:
            m.return_value = None
            self.fetch('/js/foo.js')
            m.assert_called_once_with('foo.js')

    def test_routing_database(self):
        with mock.patch.object(handlers.DatabaseHandler, 'post') as m:
            m.return_value = None
            self.fetch('/api/v1/database/cmdb', method="POST")
            m.assert_called_once_with('cmdb')

    @gen_test(timeout=3)
    def test_routing_service(self):
        with mock.patch.object(handlers.ServicesHanlder, 'get') as m:
            url = '/api/v1/cmdb/service/list'
            self.http_client.fetch(self.get_url(url))
            m.assert_called_once_with('cmdb')
        with mock.patch.object(handlers.ServiceHanlder, 'get') as m:
            url = '/api/v1/cmdb/service/192.168.1.1'
            yield self.http_client.fetch(self.get_url(url))
            m.assert_called_once_with('cmdb', '192.168.1.1')
