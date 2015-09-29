#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
# from mock import patch
from tornado import web
from tornado.ioloop import IOLoop
from tornado.escape import json_encode, json_decode, url_escape
from tornado.concurrent import Future
from tornado.testing import AsyncHTTPTestCase
from tornado.testing import gen_test

from cmdb.orm_couch import Service, Project


class TestApplication(web.Application):
    def __init__(self):
        from cmdb.url import handlers
        settings = dict(debug=True)
        super(TestApplication, self).__init__(handlers, **settings)


class TestServiceHandlers(AsyncHTTPTestCase):
    def get_app(self):
        return TestApplication()

    def setUp(self):
        super(TestServiceHandlers, self).setUp()
        self.service_id = '111.222.333.444:8080'
        self.f = Future()
        self.service = Service()
        self.service.set_db('cmdb')
        # self.service_id_not_default_port = '172.16.200.999:9090'
        # self.ids = r'["172.16.200.105:8080"]'

    # @patch.object(CouchBase, 'list_ids')
    # @gen_test(timeout=5)
    # def test_root(self, mock_list_ids):
    #     self.f.set_result(self.ids)
    #     mock_list_ids.return_value = self.f
    #     response = yield self.http_client.fetch(self.get_url('/'))
    #     self.assertEqual(self.ids, response.body.decode('string-escape').strip('"'))

    def get_new_ioloop(self):
        # AsyncHTTPTestCase creates its own local IOLoop
        # any test case function should use it
        # https://github.com/tornadoweb/tornado/issues/663
        return IOLoop.instance()

    @gen_test(timeout=3)
    def tearDown(self):
        yield self.service.del_doc(self.service_id)

    @gen_test(timeout=3)
    def test_service_list(self):
        yield self.service.add_service(self.service_id, {"type": "service"})
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/_list'),
            method="GET"
        )
        r = json_decode(response.body)
        self.assertEqual(r, [self.service_id])

    @gen_test(timeout=3)
    def test_service_get(self):
        """ GET /api/v1/service/service_id """
        yield self.service.add_service(self.service_id, {"type": "service"})
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}'.format(self.service_id)),
            method="GET"
        )
        r = json_decode(response.body)
        self.assertEqual(r['_id'], self.service_id)

    @gen_test(timeout=5)
    def test_service_post(self):
        """ POST /api/v1/service/service_id """
        # yield self.service.add_service(self.service_id, {"type": "service"})
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}'.format(self.service_id)),
            method="POST",
            body=json_encode({"test": 123})
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=5)
    def test_service_put(self):
        """ PUT /service/service_id """
        yield self.service.add_service(self.service_id, {"type": "service"})
        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}'.format(self.service_id)),
            method="PUT",
            body=json_encode({"test": 123})
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], True)

        response = yield self.http_client.fetch(
            self.get_url('/api/v1/service/{0}'.format(self.service_id)),
            method="PUT",
            body=""
        )
        r = json_decode(response.body)
        self.assertEqual(r['ok'], False)
        self.assertEqual(r['msg'], "Request body is empty")

    @gen_test(timeout=5)
    def test_service_delete_field(self):
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
        return TestApplication()

    def setUp(self):
        super(TestProjectHandlers, self).setUp()
        self.project_id = '测试项目'
        self.project_id_es = url_escape(self.project_id)
        self.project = Project()
        self.project.set_db('cmdb')

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
