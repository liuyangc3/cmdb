#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import uuid
from tornado.web import RequestHandler, asynchronous, authenticated
from tornado.escape import json_encode, json_decode
from tornado import gen

from app.orm import CouchServer, CouchBase, Service, Project
from app.conf import couch_conf


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
        """ 解析 request.body, 支持 JSON格式 """
        content_type = self.request.headers["Content-Type"]
        if content_type.startswith("application/json"):
            return json_decode(self.request.body)
        if content_type.startswith("multipart/form-data") \
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

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def set_cors_headers(self):
        """ support CORS """
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        "accept, cache-control, origin, "
                        "x-requested-with, x-file-name, content-type")


class LoginHandler(BaseHandler):
    def get(self):
        try:
            error_message = self.get_argument("error")
            self.write('<html><body><form action="login" method="post">'
                       'Name: <input type="text" name="username">'
                       'Password: <input type="password" name="password">'
                       '<input type="submit" value="Sign in">'
                       '</form>' + error_message + '</body></html>')
        except:
            self.write('<html><body><form action="login" method="post">'
                       'Name: <input type="text" name="username">'
                       'Password: <input type="password" name="password">'
                       '<input type="submit" value="Sign in">'
                       '</form></body></html>')

    def check_user(self, username, password):
        if username == "admin" and password == "admin":
            return True
        return False

    def set_user(self, username):
        if username:
            self.set_secure_cookie("user", json_encode(username))
        else:
            self.clear_cookie("user")

    def post(self):
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        if self.check_user(username, password):
            self.set_user(username)
            self.redirect(self.get_argument("next", "/"))
        else:

            error_msg = "?error=" + "invalid name or password"
            self.redirect("/login" + error_msg)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))


class IndexHandler(BaseHandler):
    @authenticated
    def get(self):
        self.render('index.html')


class DatabasesHandler(BaseHandler):
    def initialize(self):
        self.couch = CouchServer(couch_conf['base_url'])

    @gen.coroutine
    def get(self):
        dbs = yield self.couch.list_db()
        self.write(json_encode(dbs))


class DatabaseHandler(BaseHandler):
    def initialize(self):
        self.couch = CouchServer(couch_conf['base_url'])

    @gen.coroutine
    def post(self, database):
        try:
            resp = yield self.couch.create(database)
            yield self.couch.init(database)
            self.write(resp)
        except ValueError as e:
            self.err_write(500, e)
        self.finish()

    @gen.coroutine
    def delete(self, database):
        try:
            resp = yield self.couch.delete(database)
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
        query = self.get_arguments("q")
        try:
            doc = yield self.service.get_doc(database, service_id)
            if query:
                self.write(json_encode(doc[query[0]]))
            else:
                self.write(json_encode(doc))
        except ValueError as e:
            self.err_write(500, e)
        except KeyError as e:
            e.message = 'error key: ' + e.message
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


"""
Projects Handlers
"""


class ProjectsHandler(BaseHandler):
    def initialize(self):
        self.project = Project(couch_conf['base_url'])

    @asynchronous
    @gen.coroutine
    def get(self, database):
        self.set_cors_headers()
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
        query = self.get_arguments("q")
        try:
            doc = yield self.project.get_doc(database, project_id)
            if query:
                self.write(json_encode(doc[query][0]))
            else:
                self.write(json_encode(doc))
        except ValueError as e:
            self.err_write(500, e)
        except KeyError as e:
            e.message = 'error key: ' + e.message
            self.err_write(500, e)
        self.finish()

    @asynchronous
    @gen.coroutine
    def post(self, database, project_name):
        request_body = self.project_dict.copy()
        if self.request.body:
            request_body.update(self.get_json_body_arguments())
        try:
            project_id = uuid.uuid4().get_hex()
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


"""
Search Handlers
"""


class SearchHandler(BaseHandler):
    def initialize(self):
        self.couch = CouchBase(couch_conf['base_url'])

    @asynchronous
    @gen.coroutine
    def get(self, database):
        """
        /api/v1/<database>/search?p=<project_id>
        """
        project_id = self.get_argument("p")
        resp = yield self.couch.client.fetch(
            "{0}/_design/project/_list/search/search?include_docs=true&key=\"{1}\"".format(
                database, project_id
            )
        )
        body = json_decode(resp.body)
        project_doc = yield self.couch.get_doc(database, project_id)
        del project_doc['_rev']
        del project_doc['services']
        del project_doc['type']
        body.update({"project": project_doc})
        self.write(body)
        self.finish()


class GetProjectIdHandler(BaseHandler):
    def initialize(self):
        self.couch = CouchBase(couch_conf['base_url'])

    @asynchronous
    @gen.coroutine
    def get(self, database):
        """
        /api/v1/<database>/getPidByName?q=<project_name>
        """
        project_name = self.get_argument("q")
        try:
            resp = yield self.couch.client.fetch(
                "{0}/_design/project/_list/getPidByName/list?q={1}".format(
                    database, project_name
                )
            )
            self.write(resp.body)
        except:
            self.err_write(500, "Project {0} Not Exist".format(project_name))
        self.finish()


if __name__ == '__main__':
    print(couch_conf['base_url'])
