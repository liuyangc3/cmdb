#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import mock
import unittest
from tornado import web
from tornado.ioloop import IOLoop
from tornado.escape import url_escape, json_encode
from tornado.testing import AsyncHTTPTestCase

from app.orm import Project
from test.utils import setup_func, raise_fetch


class TestSearchHandlers(AsyncHTTPTestCase):
    def get_app(self):
        from app.route import router
        return web.Application(router, {"debug": True})

    def get_new_ioloop(self):
        return IOLoop.instance()

    def setUp(self):
        super(TestSearchHandlers, self).setUp()
        self.database = 'couch_test'
        self.project_id = '测试项目'
        self.url = "/api/v1/{0}/project/{1}".format(self.database, url_escape(self.project_id))
        self.json_header = {"Content-Type": "application/json"}
        self.type = {'type': 'project'}

    def test_list_projects(self):
        # this test is for ProjectsHandler
        url = '/api/v1/couch_test/search/list'
        with mock.patch.object(Project, 'list_project') as mock_list:
            setup_func(mock_list, [self.project_id])
            self.fetch(url)
            mock_list.assert_called_once_with(self.database)