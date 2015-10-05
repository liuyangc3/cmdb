#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from tornado.web import RequestHandler, asynchronous
from tornado.httpclient import HTTPError
from tornado.escape import json_encode, json_decode
from tornado import gen

from cmdb.orm import Service, Project


def parse_args(tornado_arguments):
    body = {}
    for k, v in tornado_arguments.items():
        v = v[0]
        if ''.startswith('[') and ''.endswith(']'):
            body[k] = json_decode(v)
        else:
            body[k] = v
    return body


class BaseHandler(RequestHandler):
    def initialize(self):
        self.service = Service()
        self.project = Project()
        self.service_dict = {"type": "service"}
        self.project_dict = {"type": "project"}


class ServiceHanlder(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        # :TODO
        pass


class ServiceRegexpHanlder(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self, service_id):
        resp = yield self.service.get_doc(service_id)
        self.write(json_encode(resp))
        self.finish()

    @asynchronous
    @gen.coroutine
    def post(self, service_id):
        _dict = self.service_dict.copy()
        if self.request.body != '':
            _dict.update(parse_args(self.request.body_arguments))
        try:
            resp = yield self.service.add_service(service_id, _dict)
            self.write(resp)
        except ValueError as e:
            self.set_status(401)
            self.write('{{"ok": false, "msg": "{0}"}}'.format(e.message))
        self.finish()

    @asynchronous
    @gen.coroutine
    def put(self, service_id):
        if self.request.body:
            request_body = parse_args(self.request.body_arguments)
            resp = yield self.service.update_service(service_id, request_body)
            self.write(resp)
        else:
            self.write('{"ok": false, "msg": "Request body is empty"}')
        self.finish()

    @asynchronous
    @gen.coroutine
    def delete(self, service_id):
        resp = yield self.service.del_doc(service_id)
        self.write(resp)
        self.finish()


class ProjectHandler(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self, project_id):
        resp = yield self.project.list_ids()
        self.write(json_encode(resp))

    @asynchronous
    @gen.coroutine
    def post(self, project_id):
        request_body = self.project_dict.copy()
        if self.request.body != '':
            request_body.update(parse_args(self.request.body_arguments))
        try:
            resp = yield self.project.add_project(project_id, request_body)
            self.write(resp)
        except KeyError as e:
            self.write('{{"ok": false, "msg": "{0}"}}'.format(e.message))
        self.finish()

    @asynchronous
    @gen.coroutine
    def put(self, project_id):
        if self.request.body == '':
            self.write('{"ok": false, "msg": "Request body is empty"}')
            return
        request_body = parse_args(self.request.body_arguments)
        resp = yield self.project.update_project(project_id, request_body)
        self.write(resp)
        self.finish()
