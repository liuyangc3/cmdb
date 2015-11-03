#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals
import os
from tornado import gen
from tornado import ioloop
from tornado.httpclient import HTTPError
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.escape import json_decode

from cmdb.httpclient import CouchAsyncHTTPClient
from cmdb.conf import service_map, couch_conf


class CouchServer(object):
    """
    couchdb database operation
    """

    def __init__(self, url='http://localhost:5984', io_loop=None):
        self.base_url = url[:-1] if url.endswith('/') else url
        self.io_loop = io_loop or ioloop.IOLoop.instance()
        self.client = CouchAsyncHTTPClient(self.base_url, self.io_loop)

    @gen.coroutine
    def create(self, database):
        # if couchdb set a admin must use http auth
        # to create or delete a database
        # when create a database on a windows couchdb
        # get error: [Errno 10054]

        # allow_nonstandard_methods = True will send body with a '0'
        # this will cause a RST from couchdb server
        # here use pycurl client  instead of python socket
        client = CurlAsyncHTTPClient(io_loop=self.io_loop)
        try:
            resp = yield client.fetch(
                self.base_url + '/' + database,
                method="PUT",
                auth_username=couch_conf['user'],
                auth_password=couch_conf['passwd'],
                allow_nonstandard_methods=True
                )
            raise gen.Return(resp.body)
        except HTTPError:
            # HTTP 412: Precondition Failed
            raise ValueError('Database: {0} Exist'.format(database))

    @staticmethod
    def _get_design(root):
        design_path = os.path.join(root, 'design')
        return [os.path.join(design_path, f) for f in os.listdir(design_path)]

    @gen.coroutine
    def init(self, database):
        """
        add design document to a new database
        """
        root = os.path.join(os.path.dirname(__file__), '..')
        designs = self._get_design(root)
        for design in designs:
            design_name = os.path.basename(design).split('.')[0]
            with open(design) as f:
                doc = json_decode(f.read())
                yield self.client.fetch(
                    '{0}/_design/{1}'.format(database, design_name),
                    method="PUT",
                    body=doc,
                    auth_username=couch_conf['user'],
                    auth_password=couch_conf['passwd']
                )

    @gen.coroutine
    def delete(self, database):
        try:
            resp = yield self.client.fetch(
                database,
                method="DELETE",
                auth_username=couch_conf['user'],
                auth_password=couch_conf['passwd']
            )
            raise gen.Return(resp.body)
        except HTTPError:
            raise ValueError('Database: {0} not Exist'.format(database))

    @gen.coroutine
    def list_db(self):
        resp = yield self.client.fetch('_all_dbs', method="GET", allow_nonstandard_methods=True)
        databases = [db for db in json_decode(resp.body) if not db.startswith('_')]
        raise gen.Return(databases)


class Document(dict):
    """
    couchdb document class
    while do document[key] = value,key will trans to unicode
    """

    def __init__(self, _dict, **kwargs):
        super(Document, self).__init__(**kwargs)
        self.update(_dict)

    def __setitem__(self, key, value):
        return super(Document, self).__setitem__(unicode(key), value)


class CouchBase(object):
    """
    couchdb document operation
    """

    def __init__(self, url='http://localhost:5984', io_loop=None):
        self.url = url[:-1] if url.endswith('/') else url
        self.io_loop = io_loop or ioloop.IOLoop.instance()
        self.client = CouchAsyncHTTPClient(self.url, io_loop=self.io_loop)

    @gen.coroutine
    def list_ids(self, database):
        """ only list document id which not starts with '_' """
        resp = yield self.get_doc(database, '_all_docs')
        raise gen.Return([doc['id'] for doc in resp['rows'] if not doc['id'].startswith('_')])

    @gen.coroutine
    def get_doc(self, database, doc_id):
        """
        return Document instance
        """

        resp = yield self.client.get(database, doc_id, raise_error=False)
        if resp.code == 200:
            raise gen.Return(Document(json_decode(resp.body)))
        elif resp.code == 404:
            # {"error":"not_found","reason":"no_db_file"} for db not exist
            # {"error":"not_found","reason":"missing"} for doc not exist
            raise ValueError(json_decode(resp.body)['reason'])

    @gen.coroutine
    def has_doc(self, database, doc_id):
        try:
            resp = yield self.client.head(database, doc_id)
            raise gen.Return(resp.code == 200)
        except HTTPError:
            raise gen.Return(False)

    @gen.coroutine
    def get_doc_rev(self, database, doc_id):
        try:
            resp = yield self.client.head(database, doc_id)
            raise gen.Return(resp.headers['Etag'].strip('"'))
        except HTTPError:
            raise ValueError("Document {0} not Exist".format(doc_id))

    @gen.coroutine
    def update_doc(self, database, doc_id, doc):
        resp = yield self.client.put(database, doc_id, doc)
        raise gen.Return(resp.body.decode('utf-8'))

    @gen.coroutine
    def update_doc_field(self, database, doc_id, **fields):
        doc = yield self.get_doc(database, doc_id)
        for field, value in fields.items():
            doc[field] = value
        resp = yield self.client.put(database, doc_id, doc)
        raise gen.Return(resp.body.decode('utf-8'))

    @gen.coroutine
    def del_doc(self, database, doc_id):
        rev = yield self.get_doc_rev(database, doc_id)
        resp = yield self.client.delete(database, doc_id, rev)
        # json_decode can not decode String "True" but "true"
        # should return lowercase string "true"
        raise gen.Return("true" if resp.code == 200 else "false")


class Service(CouchBase):
    """
    service document operation
    """

    def __init__(self, url='http://localhost:5984', io_loop=None):
        super(Service, self).__init__(url, io_loop)
        self.reserved_key = ('type', 'ip', 'port')

    @staticmethod
    def check_ip_format(ip_address):
        pieces = ip_address.split('.')
        if 4 == len(pieces):
            if all(0 <= int(i) < 256 for i in pieces):
                return True
        raise ValueError('Invalid ip address {0}'.format(ip_address))

    def check_service_data(self, service_id, request_body):
        ip, port = service_id.split(':')
        values = ('service', ip, port)
        for field, value in zip(self.reserved_key, values):
            if field not in request_body:
                raise ValueError('Miss Field {0}'.format(field))
            elif request_body[field] != value:
                raise ValueError('Can not Change Value of Field: {0}'.format(field))

    @gen.coroutine
    def list_service(self, database):
        resp = yield self.get_doc(database, '_design/service/_view/list')
        services = [row['key'] for row in resp['rows']]
        raise gen.Return(services)

    @gen.coroutine
    def add_service(self, database, service_id, request_body):
        ip, port = service_id.split(':')
        self.check_ip_format(ip)
        exist = yield self.has_doc(database, service_id)
        if exist:
            raise ValueError('Service: {0} Exist'.format(service_id))

        if "name" not in request_body:
            if port not in service_map:
                raise ValueError('Unrecognized port,Must specify'
                                 ' the name field in the body')
            request_body["name"] = service_map[port]
        request_body.update({
            "_id": service_id,
            "ip": ip,
            "port": port
        })
        resp = yield self.update_doc(database, service_id, request_body)
        raise gen.Return(resp)

    @gen.coroutine
    def update_service(self, service_id, request_body):
        self.check_service_data(service_id, request_body)
        resp = yield self.update_doc(service_id, request_body)
        raise gen.Return(resp)


class Project(CouchBase):
    """
    project document operation
    """

    def __init__(self, url='http://localhost:5984', io_loop=None):
        super(Project, self).__init__(url, io_loop)
        self.reserved_key = ('type', 'services')

    @staticmethod
    def check_project_data(request_body):
        if 'type' in request_body and 'project' != request_body['type']:
            raise ValueError('Can Not Change Document Field: type')

    @gen.coroutine
    def list_project(self, database):
        """
        :param database: couchdb database name
        :return: a list contains project_id
        """
        resp = yield self.get_doc(database, '_design/project/_view/list')
        # use set
        raise gen.Return(list(set([row['key'] for row in resp['rows']])))

    @gen.coroutine
    def add_project(self, database, project_id, request_body):
        exist = yield self.has_doc(database, project_id)
        if exist:
            raise ValueError('Project: {0} Exist'.format(project_id))

        request_body.update({"_id": project_id})
        if 'services' not in request_body:
            request_body['services'] = []
        resp = yield self.update_doc(database, project_id, request_body)
        raise gen.Return(resp)

    @gen.coroutine
    def update_project(self, database, project_id, request_body):
        exist = yield self.has_doc(database, project_id)
        if not exist:
            raise ValueError('Project: {0} not Exist'.format(project_id))
        self.check_project_data(request_body)
        if 'services' in request_body:
            services = yield Service(self.url, self.io_loop).list_service(database)
            for req_service in request_body['services']:
                if req_service not in services:
                    raise ValueError('Service: {0} not exist'.format(req_service))
        resp = yield self.update_doc(database, project_id, request_body)
        raise gen.Return(resp)
