#!/usr/bin/python
# -*- coding: utf-8 -*-
from tornado.testing import AsyncTestCase, AsyncHTTPTestCase, AsyncHTTPClient
from tornado.testing import gen_test


class MyTest(AsyncTestCase):
    @gen_test(timeout=10)
    def test_something_slow(self):
        client = AsyncHTTPClient(self.io_loop)
        response = yield client.fetch("http://localhost:8005/")
        self.assertIn("FriendFeed", response.body)
