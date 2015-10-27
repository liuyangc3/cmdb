#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import mock
from tornado import web
from tornado.httpclient import HTTPError
from tornado.testing import AsyncHTTPTestCase

from cmdb.orm import CouchServer
from test.utils import setup_fetch_sync, raise_fetch


class TestServiceHanlder(AsyncHTTPTestCase):
    def get_app(self):
        from cmdb.route import router
        return web.Application(router, {"debug": True})

    def setUp(self):
        super(TestServiceHanlder, self).setUp()
        self.server = CouchServer(io_loop=self.io_loop)
        self.service_id = '1.1.1.1:8080'
        self.return_value = '{"ok":true}'

    def test_create_database(self):
        with mock.patch.object(CouchServer, 'fetch') as mock_fetch:
            setup_fetch_sync(mock_fetch, 200, self.return_value)
            self.fetch('/api/v1/database/couch_test', method="POST", body='')
            mock_fetch.assert_called_once_with('couch_test', method="PUT", body='')

    def test_create_raise(self):
        with mock.patch.object(CouchServer, 'fetch') as mock_fetch:
            raise_fetch(mock_fetch, HTTPError, 500)
            resp = self.fetch('/api/v1/database/couch_test', method="POST", body='')
            self.assertEqual(resp.body, '{"ok": false, "msg": "Database: couch_test Exist"}')

    def test_delete_database(self):
        with mock.patch.object(CouchServer, 'fetch') as mock_fetch:
            setup_fetch_sync(mock_fetch, 200, self.return_value)
            self.fetch('/api/v1/database/couch_test', method="DELETE")
            mock_fetch.assert_called_once_with('couch_test', method="DELETE")

    def test_delete_raise(self):
        with mock.patch.object(CouchServer, 'fetch') as mock_fetch:
            raise_fetch(mock_fetch, HTTPError, 500)
            resp = self.fetch('/api/v1/database/couch_test', method="DELETE")
            self.assertEqual(resp.body, '{"ok": false, "msg": "Database: couch_test not Exist"}')
