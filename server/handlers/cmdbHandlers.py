#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from tornado.web import RequestHandler, asynchronous
from tornado import gen

from ..orm_couch import Service


def json_encode(value):
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def parse_args(tornado_args):
    _dict = {}
    for k, v in tornado_args.items():
        _dict[k] = v[0]
    return _dict


class BaseHandler(RequestHandler):
    def initialize(self):
        self.couch = Service(url="http://172.16.200.51:5984/")
        self.couch.set_db('cmdb')


class H(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        resp = yield self.couch.list_ids()
        self.write(json_encode(resp))
        self.finish()


class ServiceHanlder(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        resp = yield self.couch.list_service_id()
        self.write(json_encode(resp))


class ServiceOperationHanlder(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self, _id):
        resp = yield self.couch.list_service_id()
        self.write(json_encode(resp))
        self.finish()

    @asynchronous
    @gen.coroutine
    def put(self, _id):
        data = parse_args(self.request.arguments)
        resp = yield self.couch.add_service(_id, **data)
        self.write(json_encode(resp))


    @asynchronous
    @gen.coroutine
    def delete(self, _id):
        pass

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
