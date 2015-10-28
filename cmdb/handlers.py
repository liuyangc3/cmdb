#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from tornado.web import RequestHandler, asynchronous
from tornado.escape import json_encode, json_decode
from tornado import gen
from tornado.httpclient import HTTPError

from cmdb.orm import CouchServer, Service, Project
from cmdb.conf import couch_conf


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
    def get_json_body_arguments(self):
        """ 解析 request.body, 支持 JSON格式
        """
        content_type = self.request.headers["Content-Type"]
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

    @staticmethod
    def check_database(database):
        couch = CouchServer(couch_conf['base_url'])
        try:
            couch.fetch(database)
        except HTTPError:
            raise ValueError("Database: {} not Exist".format(database))


class IndexHandler(RequestHandler):
    def get(self):
        self.render('index.html')


class DatabaseHandler(BaseHandler):
    def initialize(self):
        self.couch = CouchServer(couch_conf['base_url'])

    def post(self, database):
        try:
            resp = self.couch.create(database)
            self.write(resp)
        except ValueError as e:
            self.err_write(500, e)
        self.finish()

    def delete(self, database):
        try:
            resp = self.couch.delete(database)
            self.write(resp)
        except ValueError as e:
            self.err_write(500, e)
        self.finish()


class ServicesHanlder(BaseHandler):
    def initialize(self):
        self.service = Service(couch_conf['base_url'])

    @asynchronous
    @gen.coroutine
    def get(self, database):
        try:
            resp = yield self.service.list_service(database)
            self.write(json_encode(resp))
        except ValueError as e:
            self.err_write(500, e)
        self.finish()


class ServiceHanlder(BaseHandler):
    def initialize(self):
        self.service_dict = {"type": "service"}
        self.service = Service(couch_conf['base_url'])

    @asynchronous
    @gen.coroutine
    def get(self, database, service_id):
        try:
            resp = yield self.service.get_doc(database, service_id)
            self.write(json_encode(resp))
        except ValueError as e:
            self.err_write(500, e)
        self.finish()

    @asynchronous
    @gen.coroutine
    def post(self, database, service_id):
        request_body = self.service_dict.copy()
        if self.request.body:
            request_body.update(self.get_json_body_arguments())
        try:
            resp = yield self.service.add_service(database, service_id, request_body)
            self.write(resp)
        except ValueError as e:
            self.err_write(500, e)
        self.finish()

    @asynchronous
    @gen.coroutine
    def put(self, database, service_id):
        if self.request.body:
            request_body = self.get_json_body_arguments()
            try:
                resp = yield self.service.update_doc(database, service_id, request_body)
                self.write(resp)
            except Exception as e:
                self.err_write(500, e)
        else:
            self.err_write(500, "Request body is empty")
        self.finish()

    @asynchronous
    @gen.coroutine
    def delete(self, database, service_id):
        try:
            resp = yield self.service.del_doc(database, service_id)
            self.write('{{"ok": {0}}}'.format(resp))
        except ValueError as e:
            self.err_write(500, e)
        self.finish()


class ProjectsHandler(BaseHandler):
    def initialize(self):
        self.project = Project(couch_conf['base_url'])

    @asynchronous
    @gen.coroutine
    def get(self, database):
        try:
            resp = yield self.project.list_project(database)
            self.write(json_encode(resp))
        except ValueError as e:
            self.err_write(500, e)
        self.finish()


class ProjectHandler(BaseHandler):
    def initialize(self):
        self.project_dict = {"type": "project"}
        self.project = Project(couch_conf['base_url'])

    @asynchronous
    @gen.coroutine
    def get(self, database, project_id):
        try:
            resp = yield self.project.get_doc(database, project_id)
            self.write(json_encode(resp))
        except ValueError as e:
            self.err_write(500, e)
        self.finish()

    @asynchronous
    @gen.coroutine
    def post(self, database, project_id):
        request_body = self.project_dict.copy()
        if self.request.body:
            request_body.update(self.get_json_body_arguments())
        try:
            resp = yield self.project.add_project(database, project_id, request_body)
            self.write(resp)
        except ValueError as e:
            self.err_write(500, e)
        self.finish()

    @asynchronous
    @gen.coroutine
    def put(self, database, project_id):
        if self.request.body:
            request_body = self.get_json_body_arguments()
            try:
                resp = yield self.project.update_project(database, project_id, request_body)
                self.write(resp)
            except ValueError as e:
                self.err_write(500, e)
        else:
            self.err_write(500, "Request body is empty")
        self.finish()

    @asynchronous
    @gen.coroutine
    def delete(self, database, project_id):
        try:
            resp = yield self.project.del_doc(database, project_id)
            self.write('{{"ok": {0}}}'.format(resp))
        except ValueError as e:
                self.err_write(500, e)
        self.finish()


class ServiceSearchHandler(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self, database):
        couchdb = self.couch.use(database)
        key = self.get_argument("key")
        services = yield couchdb.list_service()
        res = [service for service in services if key in service]
        if res:
            self.write(json_encode(res))
        else:
            self.err_write(500, "Not Found Service")


class ProjectSearchHandler(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self, database):
        couchdb = self.couch.use(database)
        key = self.get_argument("key")
        projects = yield couchdb.list_project()
        res = [project for project in projects if key in project]
        if res:
            self.write(json_encode(res))
        else:
            self.err_write(500, "Not Found Project")