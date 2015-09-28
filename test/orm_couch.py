#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
# from mock import patch
# from tornado.concurrent import Future
from tornado.escape import json_decode
from tornado.httpclient import HTTPError
from tornado.testing import AsyncTestCase
from tornado.testing import gen_test

from cmdb.orm_couch import Service, Project


class TestCouchBase(AsyncTestCase):
    def setUp(self):
        super(TestCouchBase, self).setUp()  # setup io_loop
        self.couch = Service(io_loop=self.io_loop)
        self.couch.set_db('cmdb')
        self.test_ip = "test_ip"
        self.test_port = 8080
        self.service_id = "{0}:{1}".format(self.test_ip, self.test_port)

    @gen_test(timeout=3)
    def test_update_doc(self):
        response = yield self.couch.update_doc(
            self.service_id,
            {
                "type": "service",
                "name": "test",
                "ip": self.test_ip,
                "port": self.test_port
            })
        r = json_decode(response)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=3)
    def test_all_docs(self):
        response = yield self.couch._all_docs()
        r = json_decode(response)
        self.assertEqual(r['rows'][0]['value']['_id'], self.service_id)

    @gen_test(timeout=3)
    def test_list_ids(self):
        response = yield self.couch.list_ids()
        self.assertEqual(response[0], self.service_id)

    @gen_test(timeout=3)
    def test_get_doc_and_get_doc_rev(self):
        # test get_doc
        response = yield self.couch.get_doc(self.service_id)
        self.assertEqual(response['ip'], self.test_ip)
        self.assertEqual(response['port'], self.test_port)
        self.assertEqual(response['type'], 'service')
        try:
            yield self.couch.get_doc('not exist')
        except Exception as e:
            self.assertIsInstance(e, HTTPError)

        # test get_doc_rev
        rev = response['_rev']
        response = yield self.couch.get_doc_rev(self.service_id)
        self.assertEqual(response, rev)

    @gen_test(timeout=3)
    def test_has_doc(self):
        response = yield self.couch.has_doc(self.service_id)
        self.assertEqual(response, True)
        response = yield self.couch.has_doc('not exist')
        self.assertEqual(response, False)

    @gen_test(timeout=3)
    def test_del_doc(self):
        response = yield self.couch.del_doc(self.service_id)
        self.assertEqual(response, True)


class TestService(AsyncTestCase):
    def setUp(self):
        super(TestService, self).setUp()  # setup io_loop
        self.service = Service(io_loop=self.io_loop)
        self.service.set_db('cmdb')
        self.test_ip = "test_ip"
        self.service_id_with_default_port = 'test_ip:8080'
        self.service_id_not_default_port = 'test_ip:9999'

    @gen_test(timeout=3)
    def tearDown(self):
        yield self.service.del_doc(self.service_id_with_default_port)
        yield self.service.del_doc(self.service_id_not_default_port)

    @gen_test(timeout=3)
    def test_add_service(self):
        try:
            yield self.service.add_service(
                self.service_id_not_default_port, {"type": "service"})
        except Exception as e:
            self.assertIsInstance(e, ValueError)

        response = yield self.service.add_service(
            self.service_id_with_default_port, {"type": "service"}
        )
        r = json_decode(response)
        self.assertEqual(True, r["ok"])

        # if service port is not default
        # must define "name" in doc
        response = yield self.service.add_service(
            self.service_id_not_default_port, {"type": "service", "name": "test"}
        )
        r = json_decode(response)
        self.assertEqual(True, r["ok"])

        try:  # add a exist service
            yield self.service.add_service(
                self.service_id_with_default_port, {"type": "service"}
            )
        except Exception as e:
            self.assertIsInstance(e, KeyError)


class TestProject(AsyncTestCase):
    def setUp(self):
        super(TestProject, self).setUp()  # setup io_loop
        self.project = Project(io_loop=self.io_loop)
        self.project.set_db('cmdb')
        self.project_id = '测试项目'
        self.services = ['test_ip:8080', 'test_ip:9999']

    @gen_test(timeout=3)
    def test_add_project(self):
        response = yield self.project.add_project(
            self.project_id, {"type": "project"}
        )
        r = json_decode(response)
        self.assertEqual(True, r["ok"])

        try:
            yield self.project.add_project(
                self.project_id, {"type": "project"})
        except Exception as e:
            self.assertIsInstance(e, KeyError)
            self.assertEqual(e.message, 'Project exist')

    @gen_test(timeout=3)
    def test_check_service(self):
        doc = yield self.project.get_doc(self.project_id)
        _dict = {
            "type": "project",
            "no services": "test"
        }
        resp = self.project.check_service(_dict, doc)
        _doc = doc.copy()
        _doc.update(_dict)
        self.assertEqual(resp, _doc)

        # with services
        _dict = {
            "type": "project",
            "services": '["ipa:8080", "ipb:8081"]'
        }
        resp = self.project.check_service(_dict, doc)
        self.assertEqual(resp['services'], ["ipa:8080", "ipb:8081"])

        yield self.project.update_doc(self.project_id, resp)
        doc = yield self.project.get_doc(self.project_id)
        # with services
        _dict = {
            "type": "project",
            "services": '["ipc:8082"]'
        }
        resp = self.project.check_service(_dict, doc)
        self.assertEqual(resp['services'], ["ipa:8080", "ipb:8081", "ipc:8082"])

    @gen_test(timeout=3)
    def test_teardown(self):
        yield self.project.del_doc(self.project_id)