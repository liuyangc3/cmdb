#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from tornado import gen
from tornado import ioloop
from tornado.httpclient import HTTPClient
from tornado.httpclient import HTTPError
from tornado.escape import json_decode

from cmdb.utils.httpclient import CouchAsyncHTTPClient
from cmdb.conf import couch, service_map


class Document(dict):
    def __init__(self, _dict, **kwargs):
        super(Document, self).__init__(**kwargs)
        self.update(_dict)

    def __setitem__(self, key, value):
        return super(Document, self).__setitem__(unicode(key), value)


class CouchBase(object):
    def __init__(self, url, io_loop=None):
        self.url = url
        self.io_loop = io_loop or ioloop.IOLoop.instance()
        try:
            HTTPClient().fetch(self.url)
            self.client = CouchAsyncHTTPClient(self.url, self.io_loop)
        except HTTPError:
            raise ValueError('can not found database')

    @gen.coroutine
    def _all_docs(self):
        resp = yield self.client.get('_all_docs')
        raise gen.Return(resp.body)

    @gen.coroutine
    def list_ids(self):
        """ only list ids that not starts with '_' """
        res = []
        docs = yield self._all_docs()
        docs_json = json_decode(docs)
        for value in docs_json['rows']:
            _id = value['id']
            if not _id.startswith('_'):
                res.append(_id)
        raise gen.Return(res)

    @gen.coroutine
    def get_doc(self, doc_id):
        try:
            resp = yield self.client.get(doc_id)
            _dict = json_decode(resp.body)
            raise gen.Return(Document(_dict))
        except HTTPError:
            raise ValueError('Document {0} not Exist'.format(doc_id))

    @gen.coroutine
    def has_doc(self, doc_id):
        try:
            resp = yield self.client.head(doc_id)
            raise gen.Return(resp.code == 200)
        except HTTPError:
            raise gen.Return(False)

    @gen.coroutine
    def get_doc_rev(self, doc_id):
        try:
            resp = yield self.client.head(doc_id)
            raise gen.Return(resp.headers['Etag'].strip('"'))
        except HTTPError:
            raise ValueError("Document {0} not Exist".format(doc_id))

    @gen.coroutine
    def _update_doc(self, doc_id, doc):
        resp = yield self.client.put(doc_id, doc)
        raise gen.Return(resp.body.decode('utf-8'))

    @gen.coroutine
    def _update_doc_field(self, doc_id, **field):
        doc = yield self.get_doc(doc_id)
        for k, v in field.items():
            doc[k] = v
        resp = yield self.client.put(doc_id, doc)
        raise gen.Return(resp.body.decode('utf-8'))

    @gen.coroutine
    def del_doc(self, doc_id):
        rev = yield self.get_doc_rev(doc_id)
        resp = yield self.client.delete(doc_id, rev)
        raise gen.Return(resp.code == 200)


class Service(CouchBase):
    def __init__(self, url=couch['url'], io_loop=None):
        super(Service, self).__init__(url, io_loop)

    @staticmethod
    def check_ip(ip_address):
        pieces = ip_address.split('.')
        if 4 == len(pieces):
            if all(0 <= int(i) < 256 for i in pieces):
                return True
        raise ValueError('Invalid ip address {0}'.format(ip_address))

    @staticmethod
    def check_field(request_body):
        for field in ('ip', 'port', 'type'):
            if field in request_body:
                raise ValueError('Can not Change Document Field {0}'.format(field))

    @gen.coroutine
    def _add_service(self, ip, port, _dict):
        service_id = "{0}:{1}".format(ip, port)
        _dict.update({
            "_id": service_id,
            "ip": ip,
            "port": port
        })
        resp = yield self.client.put(service_id, _dict)
        raise gen.Return(resp.body)

    @gen.coroutine
    def add_service(self, service_id, _dict):
        exist = yield self.has_doc(service_id)
        if exist:
            raise KeyError('service id exist')
        ip, port = service_id.split(':')
        self.check_ip(ip)
        try:
            if "name" not in _dict:
                _dict.update({"name": service_map[port]})
            resp = yield self._add_service(ip, port, _dict)
            raise gen.Return(resp)
        except KeyError:
            raise ValueError('not found name in url argument')

    @gen.coroutine
    def update_service(self, service_id, request_body):
        doc = yield self.get_doc(service_id)
        self.check_field(request_body)
        doc.update(request_body)
        resp = yield self._update_doc(service_id, doc)
        raise gen.Return(resp)


class Project(CouchBase):
    def __init__(self, url=couch['url'], io_loop=None):
        super(Project, self).__init__(url, io_loop)

    @staticmethod
    def check_field(request_body):
        if 'type' in request_body:
            raise ValueError('Can not Change Document Field type')

    @staticmethod
    def _merge_services(request_body, doc):
        SERVICES = 'services'
        if SERVICES in request_body and SERVICES in doc:
            x = set(request_body[SERVICES])
            y = set(doc[SERVICES])
            if x & y:
                request_body[SERVICES] = list(x | y)
        doc.update(request_body)
        return doc

    @gen.coroutine
    def add_project(self, project_id, request_body):
        exist = yield self.has_doc(project_id)
        if exist:
            raise KeyError('Project exist')
        else:
            request_body.update({"_id": project_id})
            resp = yield self._update_doc(project_id, request_body)
            raise gen.Return(resp)

    @gen.coroutine
    def update_project(self, project_id, request_body):
        doc = yield self.get_doc(project_id)
        self.check_field(request_body)
        doc = self._merge_services(request_body, doc)
        resp = yield self._update_doc(project_id, doc)
        raise gen.Return(resp)

