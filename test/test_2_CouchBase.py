#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from tornado.escape import json_decode
from tornado.testing import AsyncTestCase
from tornado.testing import gen_test

from cmdb.orm import CouchServer, CouchBase


class TestCouchBase(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = CouchServer()
        cls.database = 'couch-base_test'
        cls.server.create(cls.database)
        cls.doc_ids = ["test_id_01", "test_id_02", "test_id_03"]

    @classmethod
    def tearDownClass(cls):
        cls.server = CouchServer()
        cls.database = 'couch-base_test'
        cls.server.delete(cls.database)

    def setUp(self):
        super(TestCouchBase, self).setUp()  # setup io_loop
        self.couch = CouchBase(io_loop=self.io_loop)

    @gen_test(timeout=3)
    def test_1_update_doc(self):
        for doc_id in self.doc_ids:
            doc = {"_id": doc_id}
            response = yield self.couch.update_doc(self.database, doc_id, doc)
            json = json_decode(response)
            self.assertEqual(json['ok'], True)

    @gen_test(timeout=3)
    def test_2_list_docs(self):
        doc_list = yield self.couch.list_ids(self.database)
        self.assertEqual(doc_list, self.doc_ids)

    @gen_test(timeout=3)
    def test_4_has_doc(self):
        response = yield self.couch.has_doc(self.database, "test_id_01")
        self.assertEqual(response, True)

        response = yield self.couch.has_doc(self.database, 'not exist')
        self.assertEqual(response, False)

    @gen_test(timeout=3)
    def test_5_get_doc(self):
        response = yield self.couch.get_doc(self.database, "test_id_01")
        self.assertEqual(response['_id'], "test_id_01")
        # save rev for test_6_get_doc_rev
        TestCouchBase.rev = response['_rev']
        print(TestCouchBase.rev)

        try:
            yield self.couch.get_doc(self.database, 'not exist')
        except Exception as e:
            self.assertIsInstance(e, ValueError)

    @gen_test(timeout=3)
    def test_6_get_doc_rev(self):
        rev = TestCouchBase.rev
        response = yield self.couch.get_doc_rev(self.database, "test_id_01")
        self.assertEqual(response, rev)

    @gen_test(timeout=3)
    def test_7_update_doc_field(self):
        response = yield self.couch.update_doc_field(
            self.database,
            "test_id_01",
            filed1="1.2.3.4",
            filed2=4567
        )
        r = json_decode(response)
        self.assertEqual(r['ok'], True)
        doc = yield self.couch.get_doc(self.database, "test_id_01")
        self.assertEqual(doc['filed1'], "1.2.3.4")
        self.assertEqual(doc['filed2'], 4567)

    @gen_test(timeout=3)
    def test_8_del_doc(self):
        for doc_id in self.doc_ids:
            response = yield self.couch.del_doc(self.database, doc_id)
            self.assertEqual(response, 'true')

    @gen_test(timeout=3)
    def test_9_del_doc_not_exist(self):
        try:
            yield self.couch.del_doc(self.database, 'not exist')
        except Exception as e:
            self.assertIsInstance(e, ValueError)
            self.assertEqual(e.message, 'Document {0} not Exist'.format('not exist'))
