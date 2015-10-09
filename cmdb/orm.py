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
    def _update_doc_field(self, doc_id, **fields):
        doc = yield self.get_doc(doc_id)
        for field, value in fields.items():
            doc[field] = value
        resp = yield self.client.put(doc_id, doc)
        raise gen.Return(resp.body.decode('utf-8'))

    @gen.coroutine
    def del_doc(self, doc_id):
        rev = yield self.get_doc_rev(doc_id)
        resp = yield self.client.delete(doc_id, rev)
        # json_decode can not decode "True" but "true"
        raise gen.Return("true" if resp.code == 200 else "false")


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
    def list(self):
        resp = yield self.client.get('_design/service/_view/list')
        services = []
        for row in json_decode(resp.body)['rows']:
            services.append(row['key'])
        raise gen.Return(services)

    @gen.coroutine
    def _add_service(self, ip, port, request_body):
        service_id = "{0}:{1}".format(ip, port)
        request_body.update({
            "_id": service_id,
            "ip": ip,
            "port": port
        })
        resp = yield self.client.put(service_id, request_body)
        raise gen.Return(resp.body)

    @gen.coroutine
    def add_service(self, service_id, request_body):
        exist = yield self.has_doc(service_id)
        if exist:
            raise KeyError('Service id exist')
        ip, port = service_id.split(':')
        self.check_ip(ip)
        if "name" not in request_body:
            if port not in service_map:
                raise ValueError('Unrecognized port,Must specify'
                                 ' the name field in the body')
            request_body["name"] = service_map[port]
        resp = yield self._add_service(ip, port, request_body)
        raise gen.Return(resp)

    @gen.coroutine
    def update_service(self, service_id, request_body):
        self.check_field(request_body)
        doc = yield self.get_doc(service_id)
        doc.update(request_body)
        resp = yield self._update_doc(service_id, doc)
        raise gen.Return(resp)

    @gen.coroutine
    def delete_service_field(self, service_id, fields):
        self.check_field(fields)
        doc = yield self.get_doc(service_id)
        for field in fields:
            if field not in doc:
                raise KeyError('Field {0} Not In Service {1}'.format(field, service_id))
            del doc[field]
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
        if 'services' in request_body and 'services' in doc:
            # 取提交service 集合与文档service集合的并集
            # 作为最终的service
            x = set(request_body['services'])
            y = set(doc['services'])
            if x & y:
                request_body['services'] = list(x | y)
        doc.update(request_body)
        return doc

    @gen.coroutine
    def list(self):
        resp = yield self.client.get('_design/project/_view/list?group=true')
        r = json_decode(resp.body)
        projects = []
        for row in r['rows']:
            projects.append(row['key'])
        raise gen.Return(projects)

    @gen.coroutine
    def get_project(self, project_id):
        # 父类 get_doc 返回 dict 对象
        # 这里无法使用 get_doc 取 project 信息
        try:
            resp = yield self.client.get(project_id)
            raise gen.Return(resp.body)
        except HTTPError:
            raise ValueError('Document {0} not Exist'.format(project_id))

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
