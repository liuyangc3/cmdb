#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import mock
import unittest
from tornado import web
from tornado.ioloop import IOLoop
from tornado.escape import json_encode
from tornado.testing import AsyncHTTPTestCase

from cmdb.orm import Service
from test.utils import setup_func, raise_fetch


class TestServiceHandler(AsyncHTTPTestCase):
    def get_app(self):
        from cmdb.route import router
        return web.Application(router, {"debug": True})

    def setUp(self):
        super(TestServiceHandler, self).setUp()
        self.database = 'couch_test'
        self.service_id = '1.1.1.1:9874'
        self.url = "/api/v1/{0}/service/{1}".format(self.database, self.service_id)
        self.json_header = {"Content-Type": "application/json"}
        self.type = {'type': 'service'}

    def get_new_ioloop(self):
        # AsyncHTTPTestCase creates its own local IOLoop
        # any test case function should use it
        # https://github.com/tornadoweb/tornado/issues/663
        return IOLoop.instance()

    def form_data(self, doc):
        boundary = '----WebKitFormBoundary_MyTestBoundary_'
        body = ''
        for k, v in doc.items():
            body += '--{0}\r\nContent-Disposition: form-data; name="{1}"\r\n\r\n{2}\r\n'.format(boundary, k, v)
        body += '--{0}--\r\n'.format(boundary)
        headers = {'Content-Type': 'multipart/form-data; boundary={0}'.format(boundary)}
        return headers, body

    def test_list_services(self):
        # this test is for ServicesHandler
        url = '/api/v1/couch_test/service/list'
        with mock.patch.object(Service, 'list_service') as mock_list:
            setup_func(mock_list, [self.service_id])
            self.fetch(url)
            mock_list.assert_called_once_with(self.database)

        # raise test
        with mock.patch.object(Service, 'get_doc') as mock_get:
            raise_fetch(mock_get, ValueError, 'missing')
            resp = self.fetch(url)
            self.assertEqual(resp.body, '{"ok": false, "msg": "missing"}')

    def test_1_ServiceHandler_get(self):
        with mock.patch.object(Service, 'get_doc') as mock_get:
            data = {"foo": "bar"}
            setup_func(mock_get, data)
            resp = self.fetch(self.url)
            mock_get.assert_called_once_with(self.database, self.service_id)
            self.assertEqual(resp.body, json_encode(data))

        # raise test
        with mock.patch.object(Service, 'get_doc') as mock_get:
            raise_fetch(mock_get, ValueError, 'no_db_file')
            resp = self.fetch(self.url)
            self.assertEqual(resp.code, 500)
            self.assertEqual(resp.body, '{"ok": false, "msg": "no_db_file"}')

    def test_2_ServiceHandler_post(self):
        data = {"foo": "bar"}
        data_str = json_encode(data)
        add_data = data.copy()
        add_data.update(self.type)

        # application/json
        with mock.patch.object(Service, 'add_service') as mock_add:
            setup_func(mock_add, 'ok')
            self.fetch(self.url, method="POST", headers=self.json_header, body=data_str)
            mock_add.assert_called_once_with(self.database, self.service_id, add_data)

        # multipart/form-data
        with mock.patch.object(Service, 'add_service') as mock_add:
            setup_func(mock_add, 'ok')
            headers, data = self.form_data(data)
            self.fetch(self.url, method="POST", headers=headers, body=data)
            mock_add.assert_called_once_with(self.database, self.service_id, add_data)

        # test raise
        with mock.patch.object(Service, 'add_service') as mock_add:
            raise_fetch(mock_add, ValueError, "foo")
            resp = self.fetch(self.url, method="POST", body='')
            self.assertEqual(resp.body, '{"ok": false, "msg": "foo"}')

    def test_3_ServiceHandler_put(self):
        data = {"foo": "bar"}
        data_str = json_encode(data)

        with mock.patch.object(Service, 'update_doc') as mock_up:
            setup_func(mock_up, 'ok')
            # empty body
            resp = self.fetch(self.url, method="PUT", body='')
            self.assertEqual(resp.code, 500)
            self.assertEqual(resp.body, '{"ok": false, "msg": "Request body is empty"}')
            # application/json
            self.fetch(self.url, method="PUT", headers=self.json_header, body=data_str)
            mock_up.assert_called_once_with(self.database, self.service_id, data)

        # multipart/form-data
        with mock.patch.object(Service, 'update_doc') as mock_up:
            setup_func(mock_up, 'ok')
            headers, body = self.form_data(data)
            self.fetch(self.url, method="PUT", headers=headers, body=body)
            mock_up.assert_called_once_with(self.database, self.service_id, data)

    def test_4_ServiceHandler_delete(self):
        with mock.patch.object(Service, 'del_doc') as mock_del:
            setup_func(mock_del, 'foo')
            resp = self.fetch(self.url, method="DELETE")
            mock_del.assert_called_once_with(self.database, self.service_id)
            self.assertEqual(resp.body, '{"ok": foo}')

if __name__ == '__main__':
    unittest.main()
