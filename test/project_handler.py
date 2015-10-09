#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from tornado import web
from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPRequest, HTTPError
from tornado.escape import url_escape, json_decode
from tornado.testing import AsyncHTTPTestCase
from tornado.testing import gen_test

from cmdb.orm import Service, Project


class TestProjectHandlers(AsyncHTTPTestCase):
    def get_app(self):
        from cmdb.route import router
        return web.Application(router, {"debug": True})

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
    def test_21_projects_handler_get(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/list'),
            method="GET"
        )
        projects = json_decode(response.body)
        for project in projects:
            self.assertEqual(project, self.project_id)

    @gen_test(timeout=3)
    def test_22_project_handler_get(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_escape)),
            method="GET"
        )
        r = json_decode(response.body)
        self.assertEqual(r['_id'], self.project_id)

    @gen_test(timeout=5)
    def test_31_project_handler_put_form_data(self):
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
    def test_31_project_handler_put_body_urlencoded(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_escape)),
            method="PUT",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body="field=whatever2"
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)
        doc = yield self.project.get_doc(self.project_id_escape)
        self.assertEqual(doc['field'], 'whatever2')

    @gen_test(timeout=5)
    def test_31_project_handler_put__body_json(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/project/{0}'.format(self.project_id_escape)),
            method="PUT",
            headers={"Content-Type": "application/json"},
            body='{"field":"whatever3"}'
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)
        doc = yield self.project.get_doc(self.project_id_escape)
        self.assertEqual(doc['field'], 'whatever3')

    @gen_test(timeout=5)
    def test_32_projecthandler_put_no_body(self):
        try:
            yield self.http_client.fetch(
                self.get_url('/api/v1/project/{0}'.format(self.project_id_escape)),
                method="PUT",
                body=""
            )
        except HTTPError as e:
            self.assertEqual(e.message, 'HTTP 500: Request body is empty')

    @gen_test(timeout=5)
    def test_33_projecthandler_put_add_service(self):
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
    def test_34_projecthandler_put_add_service_not_exist(self):
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
