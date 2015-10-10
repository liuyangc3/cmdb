#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from tornado.escape import json_decode
from tornado.testing import AsyncTestCase
from tornado.testing import gen_test

from cmdb.orm import Service


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
        response = yield self.couch._update_doc_field(
            self.service_id,
            ip="1.2.3.4",
            port=4567
        )
        r = json_decode(response)
        self.assertEqual(r['ok'], True)
        doc = yield self.couch.get_doc(self.service_id)
        self.assertEqual(doc['ip'], "1.2.3.4")
        self.assertEqual(doc['port'], 4567)

    @gen_test(timeout=3)
    def test_8_del_doc(self):
        response = yield self.couch.del_doc(self.service_id)
        self.assertEqual(response, 'true')

    @gen_test(timeout=3)
    def test_9_del_doc_not_exist(self):
        try:
            yield self.couch.del_doc(self.service_id)
        except Exception as e:
            self.assertIsInstance(e, ValueError)
            self.assertEqual(
                e.message,
                'Document {0} not Exist'.format(self.service_id)
            )


class TestService(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.ip = "1.1.1.1"
        cls.service_id_with_default_port = '1.1.1.1:8080'
        cls.service_id_not_default_port = '1.1.1.1:9999'
        cls.not_allowed_field = ['ip', 'port', 'type']

    def setUp(self):
        super(TestService, self).setUp()  # setup io_loop
        self.service = Service(io_loop=self.io_loop)

    def test_check_ip(self):
        self.assertEqual(self.service.check_ip(self.ip), True)
        self.assertRaises(
            ValueError,
            self.service.check_ip,
            "111.222.333.444"
        )

    def test_check_field(self):
        ip = {"ip": self.ip}
        port = {"port": 8080}
        _type = {"type": "some type"}
        self.assertRaises(ValueError, self.service.check_field, ip)
        self.assertRaises(ValueError, self.service.check_field, port)
        self.assertRaises(ValueError, self.service.check_field, _type)

    @gen_test(timeout=3)
    def test_11_add_default_port_service(self):
        response = yield self.service.add_service(
            self.service_id_with_default_port, {"type": "service"}
        )
        r = json_decode(response)
        self.assertEqual(r["ok"], True)

    @gen_test(timeout=3)
    def test_12_add_non_default_port_service_with_name_field(self):
        response = yield self.service.add_service(
            self.service_id_not_default_port, {"type": "service", "name": "test"}
        )
        r = json_decode(response)
        self.assertEqual(r["ok"], True)

    @gen_test(timeout=3)
    def test_13_add_non_default_port_service_without_name_field(self):
        try:
            yield self.service.add_service(
                self.service_id_not_default_port,
                {"type": "service"}
            )
        except Exception as e:
            self.assertIsInstance(e, ValueError)
            self.assertEqual(e.message, 'Unrecognized port,Must specify the name field in the body')

    @gen_test(timeout=3)
    def test_14_add_service_which_exist(self):
        try:
            yield self.service.add_service(
                self.service_id_with_default_port,
                {"type": "service"}
            )
        except Exception as e:
            self.assertIsInstance(e, KeyError)

    @gen_test(timeout=3)
    def test_21_list(self):
        services = yield self.service.list()
        self.assertEqual(
            services,
            [self.service_id_with_default_port,
             self.service_id_not_default_port])

    @gen_test(timeout=3)
    def test_31_update_service_not_allowed_field(self):
        for field in self.not_allowed_field:
            try:
                yield self.service.update_service(
                    self.service_id_with_default_port,
                    {field: "this change should not allowed"}
                )
            except Exception as e:
                self.assertIsInstance(e, ValueError)
                self.assertEqual(
                    e.message,
                    'Can not Change Document Field {0}'.format(field)
                )

    @gen_test(timeout=3)
    def test_32_update_service_allowed_field(self):
        resp = yield self.service.update_service(
            self.service_id_with_default_port,
            {"whatever": "this change is allowed"}
        )
        r = json_decode(resp)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=3)
    def test_41_delete_service_not_allowed_field(self):
        for field in self.not_allowed_field:
            try:
                yield self.service.delete_service_field(
                    self.service_id_with_default_port,
                    [field]
                )
            except Exception as e:
                self.assertIsInstance(e, ValueError)
                self.assertEquals(
                    e.message,
                    'Can not Change Document Field {0}'.format(field)
                )

    @gen_test(timeout=3)
    def test_42_delete_service_allowed_field(self):
        response = yield self.service.delete_service_field(
            self.service_id_with_default_port,
            ['whatever']
        )
        r = json_decode(response)
        self.assertEqual(r['ok'], True)

    @gen_test(timeout=3)
    def test_43_delete_service_field_not_exist(self):
        try:
            yield self.service.delete_service_field(
                self.service_id_with_default_port,
                ['not exist']
            )
        except Exception as e:
            self.assertIsInstance(e, KeyError)
            self.assertEqual(
                e.message,
                "Field not exist Not In Service {0}".format(self.service_id_with_default_port)
            )

    @gen_test(timeout=3)
    def test_9_end_tear_down_class(self):
        yield self.service.del_doc(self.service_id_with_default_port)
        yield self.service.del_doc(self.service_id_not_default_port)


