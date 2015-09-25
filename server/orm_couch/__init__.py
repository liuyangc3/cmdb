#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json
import tornado.ioloop
from tornado import gen
from tornado.httpclient import HTTPClient, AsyncHTTPClient, HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado.escape import json_decode, json_encode, url_escape


class CouchAsyncHTTPClient(object):
    def __init__(self, url, io_loop, fetch_args=None):
        self.url = url
        if fetch_args is None:
            self._fetch_args = dict()
        else:
            self._fetch_args = fetch_args
        self.io_loop = io_loop

        self.client = AsyncHTTPClient(self.io_loop)

    def _fetch(self, *args, **kwargs):
        fetch_args = {
            'headers': HTTPHeaders({'Content-Type': 'application/json'})
        }
        fetch_args.update(self._fetch_args)
        fetch_args.update(kwargs)
        return self.client.fetch(*args, **fetch_args)

    @gen.coroutine
    def head(self, uri):
        req = HTTPRequest(
            "{0}/{1}".format(self.url, url_escape(uri)),
            method="HEAD",
        )
        resp = yield self._fetch(req)
        raise gen.Return(resp.body)

    @gen.coroutine
    def get(self, uri):
        req = HTTPRequest(
            "{0}/{1}".format(self.url, url_escape(uri)),
            method="GET",
        )
        resp = yield self._fetch(req)
        raise gen.Return(resp)

    @gen.coroutine
    def post(self, uri, data):
        req = HTTPRequest(
            "{0}/{1}".format(self.url, url_escape(uri)),
            method="POST",
            body=data
        )
        resp = yield self._fetch(req)
        raise gen.Return(resp.body)

    @gen.coroutine
    def put(self, uri, data):
        req = HTTPRequest(
            "{0}/{1}".format(self.url, url_escape(uri)),
            method="PUT",
            body=data
        )
        resp = yield self._fetch(req, data=data)
        raise gen.Return(resp.body)


class CouchBase(object):
    def __init__(self, url="http://127.0.0.1:5984/", io_loop=None):
        self.client = None
        if not url.endswith('/'):
            url += '/'
        self.url = url

        if io_loop is None:
            self.io_loop = tornado.ioloop.IOLoop.instance()
        else:
            self.io_loop = io_loop

    def set_db(self, db_name):
        HTTPClient().fetch(self.url + db_name)
        self.client = CouchAsyncHTTPClient(self.url + db_name + '/', self.io_loop)

    @gen.coroutine
    def _all_docs(self):
        resp = yield self.client.get('_all_docs')
        raise gen.Return(json_decode(resp))

    @gen.coroutine
    def list_ids(self):
        res = []
        docs = yield self._all_docs()
        for value in docs['rows']:
            _id = value['id']
            # filter id start with _
            if not _id.startswith('_'):
                res.append(_id)
        raise gen.Return(res)

    @gen.coroutine
    def get_doc(self, doc_id):
        resp = yield self.client.get(doc_id)
        raise gen.Return(resp.body)

    @gen.coroutine
    def has_doc(self, doc_id):
        resp = yield self.client.get(doc_id)
        raise gen.Return(resp.code)

    @gen.coroutine
    def doc_rev(self, doc_id):
        resp = yield self.client.head(doc_id)
        resp_json = json_decode(resp)
        raise gen.Return(resp_json['_rev'])


class Service(CouchBase):
    doc = {"type": "service"}
    services = [
        "2181",  # zookeeper
        "3306",  # mysql
        "8080",  # tomcat
        "11211",  # memcache
        "22201",  # memcacheq
        "61616",  # activemq
    ]

    def __init__(self, url, io_loop=None):
        super(Service, self).__init__(url, io_loop)

    @gen.coroutine
    def list_service_id(self):
        res = []
        _ids = yield self.list_ids()
        for _id in _ids:
            if re.match(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,5}', _id):
                res.append(_id)
        raise gen.Return(res)

    @gen.coroutine
    def add_service(self, service_id, name=None, **kwargs):
        ip, port = service_id.split(':')
        if port not in self.services and not name:
            raise ValueError('must set service name')
        service_id = '{0}:{1}'.format(ip, port)
        doc = self.doc.copy()
        doc.update({"_id": service_id, "ip": ip, "port": port}, **kwargs)
        resp = yield self.client.put(service_id, json_encode(doc))
        raise gen.Return(resp)

    def update_service(self, service_id):
        pass


class Project(object):
    doc = {"type": "project"}

    def __init__(self, couchdb):
        self.db = couchdb

    def __getitem__(self, _id):
        return self.db[_id]

    def add_project(self, project_name, services=None):
        _id = project_name
        doc = self.doc.copy()
        doc.update({"_id": _id, "services": services})
        return self.db.save(doc)

    def add_service(self, _id, service_id):
        pass

    def delete_service(self, _id, service_id):
        pass


if __name__ == '__main__':
    couch = CouchBase(url="http://172.16.200.51:5984/")
    couch.set_db('cmdb')