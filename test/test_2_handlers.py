#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import mock
import cStringIO as StringIO
from tornado import web
from tornado.ioloop import IOLoop
from tornado.concurrent import Future
from tornado.httpclient import HTTPRequest, HTTPResponse, AsyncHTTPClient
from tornado.escape import json_encode, json_decode, url_escape
from tornado.testing import AsyncHTTPTestCase
from tornado.testing import gen_test

from cmdb.orm import CouchBase, Service


class Application(web.Application):
    def __init__(self):
        from cmdb.route import router
        settings = dict(debug=True)
        super(Application, self).__init__(router, **settings)


class TestServiceRegexpHanlder(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def setUp(self):
        super(TestServiceRegexpHanlder, self).setUp()
        self.service_id = '1.1.1.1:8080'
        self.future = Future()
        self.service = Service(io_loop=self.io_loop)
        self.response = {'ok': True, 'rev': 'something'}

    def get_new_ioloop(self):
        # AsyncHTTPTestCase creates its own local IOLoop
        # any test case function should use it
        # https://github.com/tornadoweb/tornado/issues/663
        return IOLoop.instance()

    @mock.patch.object(Service, 'add_service')
    @gen_test(timeout=5)
    def test_1_post_request(self, mock_add_service):
        """ POST /api/v1/service/service_id """
        self.future.set_result(self.response)
        mock_add_service.return_value = self.future
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}'
                         .format(self.service_id)),
            method="POST",
            body=json_encode({"test": 123})
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

    @mock.patch.object(CouchBase, 'get_doc')
    @gen_test(timeout=3)
    def test_2_get_request(self, mock_get_doc):
        self.future.set_result(self.response)
        mock_get_doc.return_value = self.future
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}'
                         .format(self.service_id)),
            method="GET"
        )
        r = json_decode(response.body)
        self.assertEqual(r, [self.service_id])

    @mock.patch.object(Service, 'update_service')
    @gen_test(timeout=5)
    def test_3_put_request(self, mock_update_service):
        """ PUT /service/service_id """
        self.future.set_result('{"ok":true}')
        mock_update_service.return_value = self.future
        boundary ='----WebKitFormBoundaryoQWBjMBGzd12uIWA'
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}'.format(self.service_id)),
            method="PUT",
            headers={'Content-Type': 'multipart/form-data; boundary={0}'.format(boundary)},
            body='--{0}\r\nContent-Disposition: form-data; name="test"\r\n\r\n'
                 'whatever\r\n'
                 '--{0}--\r\n'.format(boundary)
        )
        self.assertEqual(response.body, '{"ok":true}')
        print(response.body)

    @gen_test(timeout=3)
    def test_3_put_request_no_body(self):
        """ PUT /service/service_id """
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}'.format(self.service_id)),
            method="PUT",
            body=''
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], False)
        self.assertEqual(r['msg'], 'Request body is empty')

    @gen_test(timeout=5)
    def test_4_delete_service(self):
        """ DELETE /service/service_id """
        yield self.service.add_service(self.service_id, {"type": "service", "delete": 1})
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}?field=delete'.format(self.service_id)),
            method="DELETE"
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}?field=not_exist'.format(self.service_id)),
            method="DELETE"
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], False)
        self.assertEqual(r['msg'], "fields [u'not_exist'] Not Found")

    @gen_test(timeout=5)
    def test_service_delete_all(self):
        yield self.service.add_service(self.service_id, {"type": "service", "delete": 1})
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}?all'.format(self.service_id)),
            method="DELETE"
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)
        self.assertEqual(r['msg'], "Service deleted")

        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}?all'.format(self.service_id)),
            method="DELETE"
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], False)
        self.assertEqual(r['msg'], "Service Not Found")

        # against teardown
        yield self.service.add_service(self.service_id, {"type": "service", "delete": 1})


class TestProjectHandlers(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def setUpClass(self):
        super(TestProjectHandlers, self).setUp()
        self.project_id = '测试项目'
        self.project_id_es = url_escape(self.project_id)
        self.project = Project()

    def get_new_ioloop(self):
        return IOLoop.instance()

    @gen_test(timeout=3)
    def tearDown(self):
        yield self.project.del_doc(self.project_id)

    @gen_test(timeout=3)
    def test_project_get(self):
        yield self.project.add_project(self.project_id, {"type": "project"})
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_es)),
            method="GET"
        )
        r = json_decode(response.body)
        self.assertEqual(r, [self.project_id])

    @gen_test(timeout=3)
    def test_project_post(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_es)),
            method="POST",
            body=""
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_es)),
            method="POST",
            body=""
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], False)
        self.assertEqual(r['msg'], 'Project exist')

    @gen_test(timeout=5)
    def test_project_put(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_es)),
            method="PUT",
            body=""
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], False)
        self.assertEqual(r['msg'], 'Project Not Found')

        yield self.project.add_project(self.project_id, {"type": "project"})
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_es)),
            method="PUT",
            body=""
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], False)
        self.assertEqual(r['msg'], 'Request body is empty')

        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_es)),
            method="PUT",
            body=json_encode({"services": '["111:8080", "222:8081"]'})
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

        yield self.http_client.fetch(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_es)),
            method="PUT",
            body=json_encode({"services": '["333:8082"]'})
        )
        response = yield self.project.get_doc(self.project_id)
        self.assertEqual(response['services'], ["222:8081", "111:8080", "333:8082"])


def setup_fetch(mock_fetch, status_code, body=None):
    def side_effect(request, **kwargs):
        if request is not HTTPRequest:
            request = HTTPRequest(request)
        _buffer = StringIO.StringIO(body)
        response = HTTPResponse(request, status_code, None, _buffer)
        future = Future()
        future.set_result(response)
        return future
    mock_fetch.side_effect = side_effect
