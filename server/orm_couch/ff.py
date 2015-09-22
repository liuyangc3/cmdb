#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import tornado.ioloop
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado.escape import json_decode, url_escape


class CouchHTTPClient(object):
    def __init__(self, url, fetch_args=None, io_loop=None):
        self.url = url
        if fetch_args is None:
            self._fetch_args = dict()
        else:
            self._fetch_args = fetch_args
        if io_loop is None:
            self.io_loop = tornado.ioloop.IOLoop.instance()
        else:
            self.io_loop = io_loop
        self._client = AsyncHTTPClient(self.io_loop)

    def _fetch(self, *args, **kwargs):
        fetch_args = {
            'headers': HTTPHeaders({'Content-Type': 'application/json'})
        }
        fetch_args.update(self._fetch_args)
        fetch_args.update(kwargs)
        return self._client.fetch(*args, **fetch_args)

    @gen.coroutine
    def _http_head(self, uri):
        req = HTTPRequest(
            "{0}/{1}".format(self.url, url_escape(uri)),
            method="HEAD",
        )
        resp = yield self._fetch(req)
        raise gen.Return(resp.body)

    @gen.coroutine
    def http_get(self, uri):
        req = HTTPRequest(
            "{0}/{1}".format(self.url, url_escape(uri)),
            method="GET",
        )
        resp = yield self._fetch(req)
        raise gen.Return(resp.body)


class CouchBase(object):
    def __init__(self, url="http://127.0.0.1:5984/"):
        if not url.endswith('/'):
            url += '/'
        self.url = url

    def __getitem__(self, db_name):
        return Database(self.url + db_name)


class Database(object):
    def __init__(self, baseurl):
        self.baseurl = baseurl
        self.client = CouchHTTPClient(baseurl)

    @gen.coroutine
    def _all_docs(self):
        resp = yield self.client.http_get('_all_docs')
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
        resp = yield self.client.http_get(doc_id)
        raise gen.Return(resp)

    def service(self):
        return Service(self.baseurl)

    def project(self):
        return Project(self.baseurl)


class Service(Database):
    doc = {"type": "service"}
    services = [
        2181,  # zookeeper
        3306,  # mysql
        8080,  # tomcat
        11211,  # memcache
        22201,  # memcacheq
        61616,  # activemq
    ]

    def __init__(self, baseurl):
        super(Service, self).__init__(baseurl)

    @gen.coroutine
    def list_service_id(self):
        res = []
        _ids = yield self.list_ids()
        for _id in _ids:
            if re.match(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,3}', _id):
                res.append(_id)
        raise gen.Return(res)

    @gen.coroutine
    def add(self, ip, port, **kwargs):
        pass
    #     _id = "{0}:{1}".format(ip, port)
    #     if port not in self.services:
    #         raise ValueError('need argument name=service_name')
    #     doc = self.doc.copy()
    #     doc.update({"_id": _id, "ip": ip, "port": port})
    #     for key in kwargs:
    #         doc[key] = kwargs[key]
    #     return self.db.save(doc)
    #
    # def update(self, _id, **kwargs):
    #     doc = self.db[_id]
    #     for key in kwargs:
    #         doc[key] = kwargs[key]
    #     return self.db.save(doc)


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
