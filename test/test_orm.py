#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from tornado.escape import json_decode
from tornado.testing import AsyncTestCase
from tornado.testing import gen_test

from cmdb.orm import Service, Project


class TestCouchBase(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.ip = "1.1.1.1"
        cls.port = 8080
        cls.service_id = "{0}:{1}".format(cls.ip, cls.port)

    def setUp(self):
        super(TestCouchBase, self).setUp()  # setup io_loop
        self.couch = Service(io_loop=self.io_loop)

    @gen_test(timeout=3)
    def test_1_update_doc(self):
        response = yield self.couch._update_doc(
            self.service_id,
            {
                "type": "service",
                "name": "test",
                "ip": self.ip,
                "port": self.port
            })
        r = json_decode(response)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=3)
    def test_2_all_docs(self):
        response = yield self.couch._all_docs()
        r = json_decode(response)
        self.assertEqual(r['rows'][0]['id'], self.service_id)

    @gen_test(timeout=3)
    def test_3_list_ids(self):
        response = yield self.couch.list_ids()
        self.assertEqual(response[0], self.service_id)

    @gen_test(timeout=3)
    def test_4_has_doc(self):
        response = yield self.couch.has_doc(self.service_id)
        self.assertEqual(response, True)
        response = yield self.couch.has_doc('not exist')
        self.assertEqual(response, False)

    @gen_test(timeout=3)
    def test_5_get_doc(self):
        response = yield self.couch.get_doc(self.service_id)
        self.assertEqual(response['ip'], self.ip)
        self.assertEqual(response['port'], self.port)
        self.assertEqual(response['type'], 'service')
        try:
            yield self.couch.get_doc('a doc not exist')
        except Exception as e:
            self.assertIsInstance(e, ValueError)

    @gen_test(timeout=3)
    def test_6_get_doc_rev(self):
        before = yield self.couch.get_doc(self.service_id)
        response = yield self.couch.get_doc_rev(self.service_id)
        self.assertEqual(response, before['_rev'])

    @gen_test(timeout=3)
    def test_7_update_doc_field(self):
        response = yield self.couch._update_doc_field(self.service_id, ip="1.2.3.4", port=4567)
        r = json_decode(response)
        self.assertEqual(r['ok'], True)
        doc = yield self.couch.get_doc(self.service_id)
        self.assertEqual(doc['ip'], "1.2.3.4")
        self.assertEqual(doc['port'], 4567)

    @gen_test(timeout=3)
    def test_8_del_doc(self):
        response = yield self.couch.del_doc(self.service_id)
        self.assertEqual(response, True)
        try:
            yield self.couch.del_doc(self.service_id)
        except Exception as e:
            self.assertIsInstance(e, ValueError)
            self.assertEqual(e.message,
                             'Document {0} not Exist'.format(self.service_id))


class TestService(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.ip = "1.1.1.1"
        cls.service_id_with_default_port = '1.1.1.1:8080'
        cls.service_id_not_default_port = '1.1.1.1:9999'

    def setUp(self):
        super(TestService, self).setUp()  # setup io_loop
        self.service = Service(io_loop=self.io_loop)

    def test_check_ip(self):
        self.assertEqual(self.service.check_ip(self.ip), True)

    def test_check_field(self):
        ip = {"ip": self.ip}
        port = {"port": 8080}
        _type = {"type": "some type"}
        self.assertRaises(ValueError, self.service.check_field, ip)
        self.assertRaises(ValueError, self.service.check_field, port)
        self.assertRaises(ValueError, self.service.check_field, _type)

    @gen_test(timeout=3)
    def test_1_add_service_not_set_name(self):
        try:
            yield self.service.add_service(
                self.service_id_not_default_port,
                {"type": "service"}
            )
        except Exception as e:
            self.assertIsInstance(e, ValueError)

    @gen_test(timeout=3)
    def test_2_add_service_with_default_port(self):
        response = yield self.service.add_service(
            self.service_id_with_default_port, {"type": "service"}
        )
        r = json_decode(response)
        self.assertEqual(True, r["ok"])

    @gen_test(timeout=3)
    def test_3_add_service_not_with_default_port(self):
        response = yield self.service.add_service(
            self.service_id_not_default_port, {"type": "service", "name": "test"}
        )
        r = json_decode(response)
        self.assertEqual(True, r["ok"])

    @gen_test(timeout=3)
    def test_4_add_service_again(self):
        try:
            yield self.service.add_service(
                self.service_id_with_default_port,
                {"type": "service"}
            )
        except Exception as e:
            self.assertIsInstance(e, KeyError)

    @gen_test(timeout=3)
    def test_5_update_service_type_field(self):
        try:
            yield self.service.update_service(
                self.service_id_with_default_port,
                {"type": "this change should not allowed"}
            )
        except Exception as e:
            self.assertIsInstance(e, ValueError)
            self.assertEquals(e.message, 'Can not Change Document Field type')

    @gen_test(timeout=3)
    def test_6_update_service_ip_field(self):
        try:
            yield self.service.update_service(
                self.service_id_with_default_port,
                {"ip": "this change should not allowed"}
            )
        except Exception as e:
            self.assertIsInstance(e, ValueError)
            self.assertEquals(e.message, 'Can not Change Document Field ip')

    @gen_test(timeout=3)
    def test_7_update_service_ip_field(self):
        try:
            yield self.service.update_service(
                self.service_id_with_default_port,
                {"port": "this change should not allowed"}
            )
        except Exception as e:
            self.assertIsInstance(e, ValueError)
            self.assertEquals(e.message, 'Can not Change Document Field port')

    @gen_test(timeout=3)
    def test_8_update_service_other_field(self):
        resp = yield self.service.update_service(
            self.service_id_with_default_port,
            {"else": "this change is allowed"}
        )
        r = json_decode(resp)
        self.assertEquals(r['ok'], True)

    @gen_test(timeout=3)
    def test_9_clean(self):
        yield self.service.del_doc(self.service_id_with_default_port)
        yield self.service.del_doc(self.service_id_not_default_port)


class TestProject(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_id = "测试项目"
        cls.services = ["ip:8080", "ip:9999"]
        cls.SERVICES = 'services'

    def setUp(self):
        super(TestProject, self).setUp()  # setup io_loop
        self.project = Project(io_loop=self.io_loop)

    @gen_test(timeout=3)
    def test_1_add_project(self):
        response = yield self.project.add_project(
            self.project_id, {"type": "project"}
        )
        r = json_decode(response)
        self.assertEqual(True, r["ok"])

    @gen_test(timeout=3)
    def test_2_add_project_again(self):
        try:
            yield self.project.add_project(
                self.project_id, {"type": "project"})
        except Exception as e:
            self.assertIsInstance(e, KeyError)
            self.assertEqual(e.message, "Project exist")

    @gen_test(timeout=3)
    def test_3_update_project(self):
        request_body = {
            self.SERVICES: self.services
        }
        resp = yield self.project.update_project(self.project_id, request_body)
        r = json_decode(resp)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=3)
    def test_3_update_project_type_field(self):
        request_body = {
            "type": "other"
        }
        try:
            yield self.project.update_project(self.project_id, request_body)
        except Exception as e:
            self.assertIsInstance(e, ValueError)
            self.assertEqual(e.message, 'Can not Change Document Field type')

    @gen_test(timeout=3)
    def test_4_get_project(self):
        TestProject.doc = yield self.project.get_doc(self.project_id)

    def test_5_merge_services(self):
        doc = TestProject.doc
        request_body = {
            "no services field": "test"
        }
        resp = self.project._merge_services(request_body, doc)
        _doc = doc.copy()
        _doc.update(request_body)
        self.assertEqual(resp, _doc)

    def test_5_merge_services_with_services_field(self):
        doc = TestProject.doc
        request_field = ["ip:8080", "ip:5566"]
        request_body = {
            self.SERVICES: request_field
        }
        resp = self.project._merge_services(request_body, doc)
        self.assertEqual(resp[self.SERVICES], list(set(request_field) | set(self.services)))

    @gen_test(timeout=3)
    def test_6_update_project_with_new_services(self):
        request_field = ["ip:8080", "ip:9999", "ip:5566"]
        request_body = {
            self.SERVICES: request_field
        }
        resp = yield self.project.update_project(self.project_id, request_body)
        r = json_decode(resp)
        self.assertEqual(r['ok'], True)
        resp = yield self.project.get_doc(self.project_id)
        self.assertEqual(resp[self.SERVICES], list(set(request_field) | set(self.services)))

    @gen_test(timeout=3)
    def test_8_clean(self):
        yield self.project.del_doc(self.project_id)