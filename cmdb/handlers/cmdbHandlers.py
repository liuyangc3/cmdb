#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from tornado.web import RequestHandler, asynchronous
from tornado.httpclient import HTTPError
from tornado.escape import json_encode, json_decode
from tornado import gen

from cmdb.orm_couch import Service, Project


def parse_args(tornado_arguments):
    _dict = {}
    for k, v in tornado_arguments.items():
        _dict[k] = v[0]
    return _dict


class BaseHandler(RequestHandler):
    def initialize(self):
        self.service = Service()
        self.service.set_db('cmdb')
        self.project = Project()
        self.project.set_db('cmdb')
        self.service_dict = {"type": "service"}
        self.project_dict = {"type": "project"}


class ServiceHanlder(BaseHandler):
    @asynchronous
    @gen.coroutine
    def get(self):
        resp = yield self.service.list_service_id()
        self.write(json_encode(resp))


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
            self.write('{{"ok": false, "msg": "{0}"}}'.format(e.message))
        self.finish()

    @asynchronous
    @gen.coroutine
    def put(self, service_id):
        try:
            doc = yield self.service.get_doc(service_id)
            if self.request.body != '':
                doc.update(parse_args(self.request.body_arguments))
                resp = yield self.service.update_doc(service_id, doc)
                self.write(resp)
            else:
                self.write('{"ok": false, "msg": "Request body is empty"}')
        except HTTPError:
            self.write('{"ok": false, "msg": "Service Not Found"}')
        self.finish()

    @asynchronous
    @gen.coroutine
    def delete(self, service_id):
        del_service = self.get_arguments('all')
        if del_service:
            try:
                resp = yield self.service.del_doc(service_id)
                if resp:
                    self.write('{"ok": true, "msg": "Service deleted"}')
            except HTTPError:
                self.write('{"ok": false, "msg": "Service Not Found"}')
            self.finish()
            return

        fields = self.get_arguments('field')
        if fields:
            fields_exist = False
            doc = yield self.service.get_doc(service_id)
            for field in fields:
                if field in doc:
                    fields_exist = True
                    del doc[field]
            if fields_exist:
                resp = yield self.service.update_doc(service_id, doc)
                self.write(resp)
            else:
                self.write('{{"ok": false, "msg": "fields {0} Not Found"}}'.format(fields))
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
        _dict = self.project_dict.copy()
        if self.request.body != '':
            _dict.update(parse_args(self.request.body_arguments))
        try:
            resp = yield self.project.add_project(project_id, _dict)
            self.write(resp)
        except KeyError as e:
            self.write('{{"ok": false, "msg": "{0}"}}'.format(e.message))
        self.finish()

    @asynchronous
    @gen.coroutine
    def put(self, project_id):
        try:
            doc = yield self.service.get_doc(project_id)
            if self.request.body != '':
                _dict = json_decode(self.request.body)
                doc = self.project.check_service(_dict, doc)
                resp = yield self.project.update_doc(project_id, doc)
                self.write(resp)
            else:
                self.write('{"ok": false, "msg": "Request body is empty"}')
        except HTTPError:
            self.write('{"ok": false, "msg": "Project Not Found"}')
        self.finish()
