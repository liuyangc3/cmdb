#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import mock
import unittest
from tornado import web
from tornado.ioloop import IOLoop
from tornado.escape import url_escape, json_encode
from tornado.testing import AsyncHTTPTestCase

from cmdb.orm import Project
from test.utils import setup_func, raise_fetch


class TestProjectHandlers(AsyncHTTPTestCase):
    def get_app(self):
        from cmdb.route import router
        return web.Application(router, {"debug": True})

    def get_new_ioloop(self):
        return IOLoop.instance()

    def setUp(self):
        super(TestProjectHandlers, self).setUp()
        self.database = 'couch_test'
        self.project_id = '测试项目'
        self.url = "/api/v1/{0}/project/{1}".format(self.database, url_escape(self.project_id))
        self.json_header = {"Content-Type": "application/json"}
        self.type = {'type': 'project'}

    def form_data(self, doc):
        boundary = '----WebKitFormBoundary_MyTestBoundary_'
        body = ''
        for k, v in doc.items():
            body += '--{0}\r\nContent-Disposition: form-data; name="{1}"\r\n\r\n{2}\r\n'.format(boundary, k, v)
        body += '--{0}--\r\n'.format(boundary)
        headers = {'Content-Type': 'multipart/form-data; boundary={0}'.format(boundary)}
        return headers, body

    def test_list_projects(self):
        # this test is for ProjectsHandler
        url = '/api/v1/couch_test/project/list'
        with mock.patch.object(Project, 'list_project') as mock_list:
            setup_func(mock_list, [self.project_id])
            self.fetch(url)
            mock_list.assert_called_once_with(self.database)

        # raise test
        with mock.patch.object(Project, 'get_doc') as mock_get:
            raise_fetch(mock_get, ValueError, 'missing')
            resp = self.fetch(url)
            self.assertEqual(resp.body, '{"ok": false, "msg": "missing"}')

    def test_1_ProjectHandler_get(self):
        with mock.patch.object(Project, 'get_doc') as mock_get:
            setup_func(mock_get, 'ok')
            self.fetch(self.url)
            mock_get.assert_called_once_with(self.database, self.project_id)

        # raise test
        with mock.patch.object(Project, 'get_doc') as mock_get:
            raise_fetch(mock_get, ValueError, 'foo')
            resp = self.fetch(self.url)
            self.assertEqual(resp.body, '{"ok": false, "msg": "foo"}')

    def test_2_ProjectHandler_post(self):
        data = {"foo": "bar"}
        data_str = json_encode(data)
        add_data = data.copy()
        add_data.update(self.type)

        # application/json
        with mock.patch.object(Project, 'add_project') as mock_add:
            setup_func(mock_add, 'ok')
            self.fetch(self.url, method="POST", headers=self.json_header, body=data_str)
            mock_add.assert_called_once_with(self.database, self.project_id, add_data)

        # multipart/form-data
        with mock.patch.object(Project, 'add_project') as mock_add:
            setup_func(mock_add, 'ok')
            headers, data = self.form_data(data)
            self.fetch(self.url, method="POST", headers=headers, body=data)
            mock_add.assert_called_once_with(self.database, self.project_id, add_data)

        # raise test
        with mock.patch.object(Project, 'add_project') as mock_add:
            raise_fetch(mock_add, ValueError, 'foo')
            resp = self.fetch(self.url, method="POST", body='')
            self.assertEqual(resp.body, '{"ok": false, "msg": "foo"}')

    def test_3_ProjectHandler_put(self):
        data = {"foo": "bar"}
        data_str = json_encode(data)
        with mock.patch.object(Project, 'update_project') as mock_up:
            setup_func(mock_up, 'ok')
            resp = self.fetch(self.url, method="PUT", body='')
            self.assertEqual(resp.body, '{"ok": false, "msg": "Request body is empty"}')
            # application/json
            self.fetch(self.url, method="PUT", headers=self.json_header, body=data_str)
            mock_up.assert_called_once_with(self.database, self.project_id, data)

        # multipart/form-data
        with mock.patch.object(Project, 'update_project') as mock_up:
            setup_func(mock_up, 'ok')
            headers, body = self.form_data(data)
            self.fetch(self.url, method="PUT", headers=headers, body=body)
            mock_up.assert_called_once_with(self.database, self.project_id, data)

    def test_4_ProjectHandler_delete(self):
        with mock.patch.object(Project, 'del_doc') as mock_del:
            setup_func(mock_del, 'foo')
            resp = self.fetch(self.url, method="DELETE")
            mock_del.assert_called_once_with(self.database, self.project_id)
            self.assertEqual(resp.body, '{"ok": foo}')


if __name__ == '__main__':
    unittest.main()