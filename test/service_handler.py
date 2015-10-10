#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import cStringIO as StringIO
from tornado import web
from tornado.ioloop import IOLoop
from tornado.concurrent import Future
from tornado.httpclient import HTTPRequest, HTTPResponse, HTTPError
from tornado.escape import json_decode
from tornado.testing import AsyncHTTPTestCase
from tornado.testing import gen_test

from cmdb.orm import Service


class TestServiceHanlder(AsyncHTTPTestCase):
    def get_app(self):
        from cmdb.route import router
        return web.Application(router, {"debug": True})

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
    def test_11_servicehandler_post_not_default_port(self):
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
    def test_12_service_handler_post_default_port(self):
        req = self.form_data_request(
            self.get_url('/api/v1/service/{0}'.format(self.service_id)),
            method="POST",
            field="whatever"
        )
        response = yield self.http_client.fetch(req)
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=5)
    def test_13_service_handler_post_service_exist(self):
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

    @gen_test(timeout=5)
    def test_14_service_handler_post_body_is_json(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/9.9.9.9:8080'),
            method="POST",
            headers={"Content-Type": "application/json"},
            body='{"json":"whatever"}'
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=5)
    def test_15_service_handler_post_body_is_urlencoded(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/9.9.9.9:3306'),
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body="f1=f1&f2=f2"
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=3)
    def test_2_get_request(self):
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}'.format(self.service_id)),
            method="GET"
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

    @gen_test(timeout=5)
    def test_9_clean(self):
        yield self.http_client.fetch(
            self.get_url('/api/v1/service/9.9.9.9:8080'),
            method="DELETE"
        )
        yield self.http_client.fetch(
            self.get_url('/api/v1/service/9.9.9.9:3306'),
            method="DELETE"
        )


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
