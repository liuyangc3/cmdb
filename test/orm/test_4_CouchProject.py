#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import mock
from tornado.escape import json_decode
from tornado.testing import AsyncTestCase
from tornado.testing import gen_test

from cmdb.orm import CouchServer, Service, Project
from test.utils import setup_func


class TestProject(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = CouchServer()
        cls.database = 'couch-project_test'
        cls.server.create(cls.database)
        cls.project_id = "测试项目"
        cls.service_id = "192.168.99.100:8080"

    @classmethod
    def tearDownClass(cls):
        cls.server = CouchServer()
        cls.database = 'couch-project_test'
        cls.server.delete(cls.database)

    def setUp(self):
        super(TestProject, self).setUp()  # setup io_loop
        self.project = Project(io_loop=self.io_loop)
        self.doc = {"type": "project"}

    def test_check_project_data(self):
        doc = {"type": "foo"}
        self.assertRaises(ValueError, self.project.check_project_data, doc)
        try:
            self.project.check_project_data(doc)
        except ValueError as e:
            self.assertEqual(e.message, 'Can Not Change Document Field: type')

    @gen_test(timeout=3)
    def test_1_add_project(self):
        response = yield self.project.add_project(
            self.database,
            self.project_id,
            self.doc
        )
        self.assertEqual(json_decode(response)["ok"], True)

        # add project again
        try:
            yield self.project.add_project(
                self.database,
                self.project_id,
                self.doc
            )
        except KeyError as e:
            self.assertEqual(e.message, "Project: {0} Exist".format(self.project_id))

    @gen_test(timeout=5)
    def test_2_list_project(self):
        # add design
        path = os.path.dirname(__file__)
        filepath = os.path.join(path, '../../design/project.json')
        with open(filepath) as f:
            doc = json_decode(f.read())
        yield self.project.update_doc(self.database, '_design/project', doc)

        projects = yield self.project.list_project(self.database)
        self.assertEqual(projects, [self.project_id])

    @gen_test(timeout=3)
    def test_31_update_project(self):
        rev = yield self.project.get_doc_rev(self.database, self.project_id)
        doc = {'_rev': rev, 'services': [self.service_id]}
        with mock.patch.object(Service, 'list_service') as mock_list:
            setup_func(mock_list, [self.service_id])
            resp = yield self.project.update_project(self.database, self.project_id, doc)
            self.assertEqual(json_decode(resp)['ok'], True)

    @gen_test(timeout=3)
    def test_32_update_project_type_field(self):
        doc = {"type": "should not change the field"}
        try:
            yield self.project.update_project(self.database, self.project_id, doc)
        except Exception as e:
            self.assertIsInstance(e, ValueError)
            self.assertEqual(e.message, 'Can Not Change Document Field: type')

