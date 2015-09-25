#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from tornado.web import RequestHandler,asynchronous
from tornado import gen

# from orm.deployment import get_project_service
# from orm.cmdb import get_service_info
# ff.CouchBase as CouchBase
# from couchdbs.f import CouchBase
from ..orm_couch.ff import CouchBase
# from  orm_couch.ff import CouchBase


def json_encode(value):
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


class BaseHandler(RequestHandler):
    def initialize(self):
        self.couch = CouchBase(url="http://172.16.200.51:5984/")
        self.cmdb = self.couch['cmdb']
        self.service = self.cmdb.service()
        self.project = self.cmdb.project()


class H(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        resp = yield self.cmdb.list_ids()
        print(json_encode(resp))
        self.write(json_encode(resp))
        self.finish()


class S(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        resp = yield self.service.list_service_id()
        self.write(json_encode(resp))
        self.finish()


# class ProjectHandler(RequestHandler):
#     def get(self, project_name, service_name):
#         self.write(
#             json.dumps(get_project_service(project_name, service_name))
#         )
#
#
# class ServicesHandler(RequestHandler):
#     def get(self, service_name):
#         pass
#
#
# class ServiceHandler(RequestHandler):
#     def get(self, ip, port):
#         self.write(json.dumps(
#             get_service_info(ip, port)
#         ))
