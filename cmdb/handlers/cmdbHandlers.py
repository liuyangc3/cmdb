#!/usr/bin/python
# -*- coding: utf-8 -*-

from tornado.web import RequestHandler, asynchronous
from tornado.escape import json_encode, json_decode
from tornado import gen

from cmdb.orm_couch import Service


def parse_args(tornado_arguments):
    _dict = {}
    for k, v in tornado_arguments.items():
        _dict[k] = v[0]
    return _dict


class BaseHandler(RequestHandler):
    def initialize(self):
        self.couch = Service()
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


class ServiceRegexpHanlder(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self, _id):
        resp = yield self.couch.get_doc(_id)
        self.write(json_encode(resp))
        self.finish()

    @asynchronous
    @gen.coroutine
    def post(self, _id):
        # data = parse_args(self.request.arguments)
        data = parse_args(self.request.body_arguments)
        resp = yield self.couch.add_service(_id, data)
        self.write(resp)
        self.finish()

    @asynchronous
    @gen.coroutine
    def put(self, _id):
        data = json_decode(self.request.body)
        resp = yield self.couch.update_doc(_id, data)
        print(resp)
        # self.write(resp.strip('"'))
        self.finish()

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
