#!/usr/bin/python
# -*- coding: utf-8 -*-
from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase
from tornado.testing import gen_test

from server.server import ApplicationWrapper
from server.orm_couch import Service


class HandlersTest(AsyncHTTPTestCase):
    def get_app(self):
        return ApplicationWrapper()

    def setUp(self):
        super(HandlersTest, self).setUp()
        self.couch = Service()
        self.couch.set_db('cmdb')

    @gen_test(timeout=5)
    def test_something_slow(self):
        response = yield self.http_client.fetch(self.get_url('/'))
        self.assertIn("FriendFeed", response.body)
