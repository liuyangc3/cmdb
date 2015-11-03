#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from tornado.testing import AsyncTestCase
from tornado.testing import gen_test

from app.httpclient import CouchAsyncHTTPClient


class TestHttpClient(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = 'couch-test'

    def setUp(self):
        super(TestHttpClient, self).setUp()  # setup io_loop
        self.client = CouchAsyncHTTPClient('http://127.0.0.1:5984/', self.io_loop)

    @gen_test(timeout=3)
    def test_get(self):
        resp = yield self.client.get(self.database, 'not exist', raise_error=False)
        self.assertEqual(resp.body, '{"error":"not_found","reason":"missing"}')

    @gen_test(timeout=3)
    def test_put(self):
        client = CouchAsyncHTTPClient('http://172.16.200.51:5984/', self.io_loop)
        resp = yield client.put('cmdb', 'foo_bar', {"foo": "bar"}, raise_error=False)
        print(resp.body)

    @gen_test(timeout=3)
    def test_fetch(self):
        # add a database without http auth
        client = CouchAsyncHTTPClient('http://172.16.200.51:5984/', self.io_loop)
        resp = yield client.fetch(
            'newcmdb',
            method="PUT",
            raise_error=False,
            allow_nonstandard_methods=True
        )
        self.assertEqual(resp.body, '{"error":"unauthorized","reason":"You are not a server admin."}')

    @gen_test(timeout=3)
    def test_fetch_auth(self):
        # add a database with http auth
        client = CouchAsyncHTTPClient('http://172.16.200.51:5984/', self.io_loop)
        resp = yield client.fetch(
            'newcmdb',
            method="PUT",
            raise_error=False,
            auth_username='admin',
            auth_password='admin',
            allow_nonstandard_methods=True
        )
        self.assertEqual(resp.body, '{"ok":true}\n')

    @gen_test(timeout=3)
    def test_fetch_del(self):
        # delete a database with http auth
        client = CouchAsyncHTTPClient('http://172.16.200.51:5984/', self.io_loop)
        resp = yield client.fetch(
            'newcmdb',
            method="DELETE",
            raise_error=False,
            auth_username='admin',
            auth_password='admin',
            allow_nonstandard_methods=True
        )
        self.assertEqual(resp.body, '{"ok":true}\n')