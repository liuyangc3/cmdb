#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
from tornado.escape import json_decode
from tornado.testing import AsyncTestCase
from tornado.testing import gen_test

from app.orm import CouchServer, Service
from app.conf import service_map


class TestCouchService(AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = CouchServer()
        cls.database = 'couch-server_test'
        cls.server.create(cls.database)

        cls.ip = "192.168.99.100"
        cls.default_ports = service_map.keys()
        cls.service_ids = ["{0}:{1}".format(cls.ip, port) for port in cls.default_ports]
        cls.non_default_port = "2015"
        cls.service_id_non_default_port = "{0}:{1}".format(cls.ip, cls.non_default_port)

    @classmethod
    def tearDownClass(cls):
        cls.server = CouchServer()
        cls.database = 'couch-server_test'
        cls.server.delete(cls.database)

    def setUp(self):
        super(TestCouchService, self).setUp()  # setup io_loop
        self.service = Service(io_loop=self.io_loop)
        self.doc = {"type": "service"}

    def test_check_ip(self):
        self.assertEqual(self.service.check_ip_format(self.ip), True)
        self.assertRaises(ValueError, self.service.check_ip_format, "111.222.333.444")

    def test_check_service_data(self):
        port = 8080
        service_id = "{0}:{1}".format(self.ip, port)
        body_miss_ip = {"port": port, "type": "service"}
        body_miss_port = {"ip": self.ip, "type": "service"}
        body_miss_type = {"ip": self.ip, "port": port}
        body_change_ip = {"ip": "1.2.3.4", "port": port, "type": "service"}
        body_change_port = {"ip": self.ip, "port": 9999, "type": "service"}
        body_change_type = {"ip": self.ip, "port": port, "type": "foo"}

        try:
            self.service.check_service_data(service_id, body_miss_ip)
        except ValueError as e:
            self.assertEqual(e.message, 'Miss Field ip')
        try:
            self.service.check_service_data(service_id, body_change_ip)
        except ValueError as e:
            self.assertEqual(e.message, 'Can not Change Value of Field: ip')

        try:
            self.service.check_service_data(service_id, body_miss_port)
        except ValueError as e:
            self.assertEqual(e.message, 'Miss Field port')
        try:
            self.service.check_service_data(service_id, body_change_port)
        except ValueError as e:
            self.assertEqual(e.message, 'Can not Change Value of Field: port')

        try:
            self.service.check_service_data(service_id, body_miss_type)
        except ValueError as e:
            self.assertEqual(e.message, 'Miss Field type')
        try:
            self.service.check_service_data(service_id, body_change_type)
        except ValueError as e:
            self.assertEqual(e.message, 'Can not Change Value of Field: type')

    @gen_test(timeout=9)
    def test_11_add_service_with_default_port(self):
        for port in self.default_ports:
            service_id = self.ip + ":" + port
            response = yield self.service.add_service(self.database, service_id, self.doc)
            self.assertEqual(json_decode(response)["ok"], True)

        # add again
        service_id = self.ip + ':8080'
        try:

            yield self.service.add_service(
                self.database,
                service_id,
                self.doc
            )
        except Exception as e:
            self.assertIsInstance(e, KeyError)
            self.assertEqual(e.message, 'Service: {0} Exist'.format(service_id))

    @gen_test(timeout=3)
    def test_12_add_non_default_port_service_with_name(self):
        response = yield self.service.add_service(
            self.database,
            self.service_id_non_default_port,
            {"type": "service", "name": "test"}
        )
        self.assertEqual(json_decode(response)["ok"], True)

    @gen_test(timeout=3)
    def test_13_add_non_default_port_service_without_name(self):
        try:
            yield self.service.add_service(
                self.database,
                self.ip + ":2016",
                self.doc
            )
        except Exception as e:
            self.assertIsInstance(e, ValueError)
            self.assertEqual(e.message, 'Unrecognized port,Must specify the name field in the body')

    @gen_test(timeout=3)
    def test_21_list(self):
        # add design
        path = os.path.dirname(__file__)
        filepath = os.path.join(path, '../../design/service.json')
        with open(filepath) as f:
            doc = json_decode(f.read())
        yield self.service.update_doc(self.database, '_design/service', doc)

        services = yield self.service.list_service(self.database)
        self.assertEqual(
            services,
            ['192.168.99.100:11211',
             '192.168.99.100:2015',
             '192.168.99.100:2181',
             '192.168.99.100:22201',
             '192.168.99.100:3306',
             '192.168.99.100:61616',
             '192.168.99.100:8080'])
