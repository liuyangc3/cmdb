#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import cStringIO as StringIO
from tornado import web
from tornado.ioloop import IOLoop
from tornado.concurrent import Future
from tornado.httpclient import HTTPRequest, HTTPResponse, HTTPError
from tornado.escape import json_encode, json_decode, url_escape
from tornado.testing import AsyncHTTPTestCase
from tornado.testing import gen_test

from cmdb.orm import Service, Project


class Application(web.Application):
    def __init__(self):
        from cmdb.route import router
        settings = dict(debug=True)
        super(Application, self).__init__(router, **settings)


class TestServiceHanlder(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def setUp(self):
        super(TestServiceHanlder, self).setUp()
        self.service_id = '1.1.1.1:8080'
        self.future = Future()
        self.service = Service(io_loop=self.io_loop)
        self.not_allowed_fields = ['type', 'ip', 'port']

    def get_new_ioloop(self):
        # AsyncHTTPTestCase creates its own local IOLoop
        # any test case function should use it
        # https://github.com/tornadoweb/tornado/issues/663
        return IOLoop.instance()

    def form_data_request(self, url, method="POST", **kwargs):
        boundary = '----WebKitFormBoundary_MyTestBoundary_'
        body = ''
        for k, v in kwargs.items():
            body += '--{0}\r\nContent-Disposition: form-data; name="{1}"\r\n\r\n{2}\r\n'.format(boundary, k, v)
        body += '--{0}--\r\n'.format(boundary)
        req = HTTPRequest(
            url,
            method=method,
            headers={'Content-Type': 'multipart/form-data; boundary={0}'.format(boundary)},
            body=body
        )
        return req

    @gen_test(timeout=5)
    def test_11_post_request_not_default_port(self):
        # 添加非默认端口的服务
        req = self.form_data_request(
            self.get_url('/api/v1/service/1.1.1.1:9874'),
            method="POST"
        )
        try:
            yield self.http_client.fetch(req)
        except Exception as e:
            self.assertEqual(
                e.message,
                'HTTP 500: Unrecognized port,Must specify the name field in the body'
            )

    @gen_test(timeout=5)
    def test_12_post_request_default_port(self):
        """ POST /api/v1/service/service_id """
        req = self.form_data_request(
            self.get_url('/api/v1/service/{0}'.format(self.service_id)),
            method="POST",
            field="whatever"
        )
        response = yield self.http_client.fetch(req)
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=5)
    def test_13_post_request_service_exist(self):
        """ POST /api/v1/service/service_id """
        req = self.form_data_request(
            self.get_url('/api/v1/service/{0}'.format(self.service_id)),
            method="POST"
        )
        try:
            yield self.http_client.fetch(req)
        except HTTPError as e:
            self.assertEqual(
                e.message,
                'HTTP 500: Service id exist'
            )

    @gen_test(timeout=3)
    def test_2_get_request(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}'
                         .format(self.service_id)),
        )
        r = json_decode(response.body)
        self.assertEqual(r['_id'], self.service_id)
        self.assertEqual(r['type'], "service")
        self.assertEqual(r['name'], "tomcat")

    @gen_test(timeout=3)
    def test_31_put_request_no_body(self):
        try:
            yield self.http_client.fetch(
                self.get_url('/api/v1/service/{0}'.format(self.service_id)),
                method="PUT",
                body=''
            )
        except HTTPError as e:
            self.assertEqual(
                e.message,
                'HTTP 500: Request body is empty'
            )

    @gen_test(timeout=5)
    def test_32_put_request_change_not_allowed_field(self):
        for field in self.not_allowed_fields:
            kw = {field: 'whatever'}
            req = self.form_data_request(
                self.get_url('/api/v1/service/{0}'.format(self.service_id)),
                method="PUT",
                **kw
            )
            try:
                yield self.http_client.fetch(req)
            except HTTPError as e:
                self.assertEqual(
                    e.message,
                    'HTTP 500: Can not Change Document Field {0}'.format(field)
                )

    @gen_test(timeout=5)
    def test_41_delete_service_field_not_exist(self):
        try:
            yield self.http_client.fetch(
                self.get_url('/api/v1/service/{0}?field=not_exist'.format(self.service_id)),
                method="DELETE"
            )
        except HTTPError as e:
            self.assertEqual(
                e.message,
                'HTTP 500: Field not_exist Not In Service {0}'.format(self.service_id)
            )

    @gen_test(timeout=5)
    def test_42_service_delete_field(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}?field=field'.format(self.service_id)),
            method="DELETE"
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=5)
    def test_43_service_delete(self):
        # delete all service
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}'.format(self.service_id)),
            method="DELETE"
        )
        r = json_decode(response.body)
        self.assertEqual(r["ok"], True)


class TestProjectHandlers(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    @classmethod
    def setUpClass(cls):
        cls.project_id = '测试项目'
        cls.project_id_escape = url_escape(cls.project_id)

    def get_new_ioloop(self):
        return IOLoop.instance()

    def setUp(self):
        super(TestProjectHandlers, self).setUp()
        self.service = Service(io_loop=self.io_loop)
        self.project = Project(io_loop=self.io_loop)

    def form_data_request(self, url, method="POST", **kwargs):
        boundary = '----WebKitFormBoundary_MyTestBoundary_'
        body = ''
        for k, v in kwargs.items():
            body += '--{0}\r\nContent-Disposition: form-data; name="{1}"\r\n\r\n{2}\r\n'.format(boundary, k, v)
        body += '--{0}--\r\n'.format(boundary)
        req = HTTPRequest(
            url,
            method=method,
            headers={'Content-Type': 'multipart/form-data; boundary={0}'.format(boundary)},
            body=body
        )
        return req

    @gen_test(timeout=3)
    def test_11_project_post(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_escape)),
            method="POST",
            body=""
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=3)
    def test_12_project_post_again(self):
        try:
            yield self.http_client.fetch(
                self.get_url('/api/v1/project/{0}'.format(self.project_id_escape)),
                method="POST",
                body=""
            )
        except HTTPError as e:
            self.assertEqual(e.message, 'HTTP 500: Project exist')

    @gen_test(timeout=3)
    def test_21_projects_get(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/list'),
            method="GET"
        )
        projects = json_decode(response.body)
        for project in projects:
            self.assertEqual(project, self.project_id)

    @gen_test(timeout=3)
    def test_22_project_get(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_escape)),
            method="GET"
        )
        r = json_decode(response.body)
        self.assertEqual(r['_id'], self.project_id)

    @gen_test(timeout=5)
    def test_31_project_put(self):
        req = self.form_data_request(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_escape)),
            method="PUT",
            field="whatever"
        )
        response = yield self.http_client.fetch(req)
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)
        doc = yield self.project.get_doc(self.project_id_escape)
        self.assertEqual(doc['field'], 'whatever')

    @gen_test(timeout=5)
    def test_32_project_put_no_body(self):
        try:
            yield self.http_client.fetch(
                self.get_url('/api/v1/project/{0}'.format(self.project_id_escape)),
                method="PUT",
                body=""
            )
        except HTTPError as e:
            self.assertEqual(e.message, 'HTTP 500: Request body is empty')

    @gen_test(timeout=5)
    def test_33_project_put_add_service(self):
        # add 2 test service
        request_body = {"type": "service"}
        service_id1 = "1.1.1.1:8080"
        service_id2 = "2.2.2.2:9090"
        yield self.service.add_service(service_id1, request_body)
        yield self.service.add_service(service_id2, request_body)

        req = self.form_data_request(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_escape)),
            method="PUT",
            services='["{0}","{1}"]'.format(service_id1, service_id2)
        )
        response = yield self.http_client.fetch(req)
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=5)
    def test_34_project_put_add_service_not_exist(self):
        req = self.form_data_request(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_escape)),
            method="PUT",
            services='["1.2.3.4:1234"]'
        )
        try:
            yield self.http_client.fetch(req)
        except HTTPError as e:
            self.assertEqual(e.message, 'HTTP 500: Service 1.2.3.4:1234 not exist')

    @gen_test(timeout=5)
    def test_35_del_33_service(self):
        yield self.service.del_doc("1.1.1.1:8080")
        yield self.service.del_doc("2.2.2.2:9090")

    @gen_test(timeout=3)
    def test_9_tearDown(self):
        yield self.project.del_doc(self.project_id)


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
