#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from tornado.web import RequestHandler, asynchronous
from tornado.escape import json_encode, json_decode
from tornado import gen

from cmdb.orm import Service, Project


def parse_args(tornado_arguments):
    body = {}
    for k, v in tornado_arguments.items():
        v = v[0]
        if v.startswith('[') and v.endswith(']'):
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

    def get_json_body_arguments(self):
        """ 解析 request.body, 支持 JSON格式
        """
        content_type = self.request.headers['Content-Type']
        if content_type.startswith("application/json"):
            return json_decode(self.request.body)
        if content_type.startswith("multipart/form-data")\
                or content_type.startswith("application/x-www-form-urlencoded"):
            # "multipart/form-data" and "application/x-www-form-urlencoded"
            # support by httputil.HTTPServerRequest
            return parse_args(self.request.body_arguments)
        raise ValueError('Unsupported Content-Type')

    def err_write(self, status_code, e):
        if isinstance(e, Exception):
            self.set_status(status_code, reason=e.message)
            self.write('{{"ok": false, "msg": "{0}"}}'.format(e.message))
        else:
            self.set_status(status_code, reason=e)
            self.write('{{"ok": false, "msg": "{0}"}}'.format(e))


class IndexHandler(RequestHandler):
    def get(self):
        self.render('index.html')


class ServicesHanlder(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        # :TODO
        pass


class ServiceHanlder(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self, service_id):
        resp = yield self.service.get_doc(service_id)
        self.write(json_encode(resp))
        self.finish()

    @asynchronous
    @gen.coroutine
    def post(self, service_id):
        request_body = self.service_dict.copy()
        if self.request.body:
            request_body.update(self.get_json_body_arguments())
        try:
            resp = yield self.service.add_service(service_id, request_body)
            self.write(resp)
        except Exception as e:
            self.err_write(500, e)
        self.finish()

    @asynchronous
    @gen.coroutine
    def put(self, service_id):
        if self.request.body:
            request_body = self.get_json_body_arguments()
            try:
                resp = yield self.service.update_service(service_id, request_body)
                self.write(resp)
            except Exception as e:
                self.err_write(500, e)
        else:
            self.err_write(500, "Request body is empty")
        self.finish()

    @asynchronous
    @gen.coroutine
    def delete(self, service_id):
        fields = self.get_arguments("field")
        if fields:
            try:
                resp = yield self.service.delete_service_field(service_id, fields)
                self.write(resp)
            except Exception as e:
                self.err_write(500, e)
        else:
            resp = yield self.service.del_doc(service_id)
            self.write('{{"ok": {0}}}'.format(resp))
        self.finish()


class ProjectsHandler(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        resp = yield self.project.list()
        self.write(json_encode(resp))
        self.finish()


class ProjectHandler(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self, project_id):
        try:
            resp = yield self.project.get_project(project_id)
            self.write(resp)
        except KeyError as e:
            self.err_write(500, e)
        self.finish()

    @asynchronous
    @gen.coroutine
    def post(self, project_id):
        request_body = self.project_dict.copy()
        if self.request.body:
            request_body.update(self.get_json_body_arguments())
        try:
            resp = yield self.project.add_project(project_id, request_body)
            self.write(resp)
        except KeyError as e:
            self.err_write(500, e)
        self.finish()

    @asynchronous
    @gen.coroutine
    def put(self, project_id):
        if self.request.body:
            request_body = self.get_json_body_arguments()
            if 'services' in request_body:
                services = yield Service().list()
                for service in request_body['services']:
                    if service not in services:
                        self.err_write(500, 'Service {0} not exist'.format(service))
            try:
                resp = yield self.project.update_project(project_id, request_body)
                self.write(resp)
            except Exception as e:
                self.err_write(500, e)
        else:
            self.err_write(500, "Request body is empty")
        self.finish()


class ServiceSearchHandler(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        key = self.get_argument("key")
        services = yield self.service.list()
        res = []
        for service_id in services:
            if key in service_id:
                res.append(service_id)
        if res:
            self.write(json_encode(res))
        else:
            self.err_write(500, "Not Found Service")


class ProjectSearchHandler(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        key = self.get_argument("key")
        projects = yield self.project.list()
        res = []
        for project_id in projects:
            if key in project_id:
                res.append(project_id)
        if res:
            self.write(json_encode(res))
        else:
            self.err_write(500, "Not Found Project")