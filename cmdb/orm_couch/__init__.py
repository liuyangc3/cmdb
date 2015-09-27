#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import tornado.ioloop
from tornado import gen
from tornado.httpclient import HTTPClient, AsyncHTTPClient
from tornado.httpclient import HTTPRequest, HTTPError
from tornado.httputil import HTTPHeaders
from tornado.escape import json_decode, json_encode, url_escape


class CouchAsyncHTTPClient(object):
    def __init__(self, url, io_loop, fetch_args=None):
        self.url = url
        self.io_loop = io_loop
        if fetch_args is None:
            self._fetch_args = dict()
        else:
            self._fetch_args = fetch_args
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
        raise gen.Return(resp)

    @gen.coroutine
    def get(self, uri):
        req = HTTPRequest(
            "{0}/{1}".format(self.url, url_escape(uri)),
            method="GET",
        )
        resp = yield self._fetch(req)
        raise gen.Return(resp)

    @gen.coroutine
    def put(self, uri, doc):
        req = HTTPRequest(
            "{0}/{1}".format(self.url, url_escape(uri)),
            method="PUT",
            body=json_encode(doc)
        )
        resp = yield self._fetch(req)
        raise gen.Return(resp)

    @gen.coroutine
    def delete(self, uri, rev):
        req = HTTPRequest(
            "{0}/{1}?rev={2}".format(self.url, url_escape(uri), rev),
            method="DELETE"
        )
        resp = yield self._fetch(req)
        raise gen.Return(resp)


class CouchBase(object):
    def __init__(self, url, io_loop=None):
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
        self.client = CouchAsyncHTTPClient(self.url + db_name, self.io_loop)

    @gen.coroutine
    def _all_docs(self):
        resp = yield self.client.get('_all_docs')
        raise gen.Return(resp.body)

    @gen.coroutine
    def list_ids(self):
        res = []
        docs = yield self._all_docs()
        docs_json = json_decode(docs)
        for value in docs_json['rows']:
            _id = value['id']
            # filter id start with _
            if not _id.startswith('_'):
                res.append(_id)
        raise gen.Return(res)

    @gen.coroutine
    def get_doc(self, doc_id):
        resp = yield self.client.get(doc_id)
        _dict = json_decode(resp.body)
        raise gen.Return(Document(_dict))

    @gen.coroutine
    def has_doc(self, doc_id):
        try:
            resp = yield self.client.head(doc_id)
            raise gen.Return(resp.code == 200)
        except HTTPError as e:
            raise gen.Return(False)

    @gen.coroutine
    def update_doc(self, doc_id, doc):
        resp = yield self.client.put(doc_id, doc)
        raise gen.Return(resp.body)

    @gen.coroutine
    def del_doc(self, doc_id):
        rev = yield self.get_doc_rev(doc_id)
        resp = yield self.client.delete(doc_id, rev)
        raise gen.Return(resp.code == 200)

    @gen.coroutine
    def get_doc_rev(self, doc_id):
        exist = yield self.has_doc(doc_id)
        if exist:
            resp = yield self.client.head(doc_id)
            raise gen.Return(resp.headers['Etag'].strip('"'))
        raise gen.Return(None)


class Document(dict):
    def __init__(self, _dict):
        self.update(_dict)

    def __setitem__(self, key, value):
        return super(Document, self).__setitem__(unicode(key), value)


class Service(CouchBase):
    doc = {"type": "service"}
    services = {
        "2181": "zookeeper",
        "3306": "mysql",
        "8080": "tomcat",
        "11211": "memcache",
        "22201": "memcacheq",
        "61616": "activemq"
    }

    def __init__(self, url="http://127.0.0.1:5984/", io_loop=None):
        super(Service, self).__init__(url, io_loop=io_loop)

    @gen.coroutine
    def list_service_id(self):
        res = []
        _ids = yield self.list_ids()
        for _id in _ids:
            if re.match(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,5}', _id):
                res.append(_id)
        raise gen.Return(res)

    @gen.coroutine
    def _add_service(self, service_id, _dict):
        ip, port = service_id.split(':')
        doc = self.doc.copy()
        doc.update({"_id": service_id, "ip": ip, "port": port})
        doc.update(_dict)
        resp = yield self.client.put(service_id, doc)
        raise gen.Return(resp.body)

    @gen.coroutine
    def add_service(self, service_id, _dict=None):
        exist = yield self.has_doc(service_id)
        if exist:
            raise KeyError('service id exist')
        else:
            port = service_id.split(':')[1]
            try:
                if not _dict:
                    _dict = {"name": self.services[port]}
                    resp = yield self._add_service(service_id, _dict)
                    raise gen.Return(resp)
                elif "name" not in _dict:
                    _dict.update({"name": self.services[port]})
                resp = yield self._add_service(service_id, _dict)
                raise gen.Return(resp)
            except KeyError as e:
                raise ValueError('not found service name in uri argument')


class Project(CouchBase):
    doc = {"type": "project"}

    def __init__(self, url="http://127.0.0.1:5984/", io_loop=None):
        super(Project, self).__init__(url, io_loop=io_loop)

    @gen.coroutine
    def add_service(self, project_id, **kwargs):
        pass

    @gen.coroutine
    def _add_project(self, project_id, **kwargs):
        doc = self.doc.copy()
        doc.update({"_id": project_id}, **kwargs)
        resp = yield self.client.put(project_id, json_encode(doc))
        raise gen.Return(resp.body)

    @gen.coroutine
    def save_project(self, project_id, **kwargs):
        exist = yield self.has_doc(project_id)
        if exist:
            resp = yield self.update_doc(project_id, **kwargs)
            raise gen.Return(resp)
        else:
            resp = yield self._add_project(project_id, **kwargs)
            raise gen.Return(resp)


if __name__ == '__main__':
    couch = CouchBase(url="http://172.16.200.51:5984/")
    couch.set_db('cmdb')
