#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from tornado.escape import json_decode
from tornado.testing import AsyncTestCase
from tornado.testing import gen_test

from cmdb.orm import Project


class TestProject(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_id = "测试项目"
        cls.services = ["8.8.8.8:8080", "9.9.9.9:9999"]
        cls.SERVICES = 'services'

    def setUp(self):
        super(TestProject, self).setUp()  # setup io_loop
        self.project = Project(io_loop=self.io_loop)

    @gen_test(timeout=3)
    def test_11_add_project(self):
        response = yield self.project.add_project(
            self.project_id, {"type": "project"}
        )
        r = json_decode(response)
        self.assertEqual(True, r["ok"])

    @gen_test(timeout=3)
    def test_12_add_project_again(self):
        try:
            yield self.project.add_project(
                self.project_id, {"type": "project"})
        except Exception as e:
            self.assertIsInstance(e, KeyError)
            self.assertEqual(e.message, "Project exist")

    @gen_test(timeout=3)
    def test_21_get_project(self):
        response = yield self.project.get_project(self.project_id)
        r = json_decode(response)
        self.assertEqual(r['_id'], self.project_id)

    @gen_test(timeout=3)
    def test_22_get_project_not_exist(self):
        _id = '不存在的项目'
        try:
            yield self.project.get_project(_id)
        except Exception as e:
            self.assertIsInstance(e, ValueError)
            self.assertEqual(e.message, "Document {0} not Exist".format(_id))

    @gen_test(timeout=3)
    def test_31_update_project(self):
        request_body = {
            self.SERVICES: self.services
        }
        resp = yield self.project.update_project(self.project_id, request_body)
        r = json_decode(resp)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=3)
    def test_32_update_project_type_field(self):
        request_body = {"type": "should not change the value"}
        try:
            yield self.project.update_project(self.project_id, request_body)
        except Exception as e:
            self.assertIsInstance(e, ValueError)
            self.assertEqual(e.message, 'Can not Change Document Field type')

    @gen_test(timeout=3)
    def test_4_prepare_project(self):
        # 获取 project doc 的 字典对象 存入全局变量 doc
        # 以便后续测试使用
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
        request_field = ["8.8.8.8:8080", "9.9.9.9:5566"]
        request_body = {
            self.SERVICES: request_field
        }
        resp = self.project._merge_services(request_body, doc)
        self.assertEqual(
            resp[self.SERVICES],
            list(set(request_field) | set(self.services))  # 取并集
        )

    @gen_test(timeout=3)
    def test_6_update_project_with_new_services(self):
        request_field = ["8.8.8.8:8080", "9.9.9.9:9999", "5.5.6.6:5566"]
        request_body = {
            self.SERVICES: request_field
        }
        resp = yield self.project.update_project(self.project_id, request_body)
        r = json_decode(resp)
        self.assertEqual(r['ok'], True)
        resp = yield self.project.get_doc(self.project_id)
        self.assertEqual(
            resp[self.SERVICES],
            list(set(request_field) | set(self.services))
        )

    @gen_test(timeout=3)
    def test_6_list(self):
        projects = yield self.project.list()
        for project in projects:
            self.assertEqual(project, self.project_id)

    @gen_test(timeout=3)
    def test_8_clean(self):
        yield self.project.del_doc(self.project_id)

    @gen_test(timeout=3)
    def test_9_list_empty(self):
        projects = yield self.project.list()
        self.assertEqual(projects, [])
