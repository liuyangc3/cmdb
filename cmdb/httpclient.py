#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals  # make format use unicode
from tornado import gen
from tornado.httpclient import HTTPRequest
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import url_escape, json_encode


class CouchAsyncHTTPClient(object):
    def __init__(self, url, io_loop):
        self.url = url
        self.client = AsyncHTTPClient(io_loop)

    def fetch(self, uri, method="GET", body=None, **kwargs):
        """
        add Content-Type in Header
        join base base_url and uri
        """
        # if "/" in uri, url_escape will turn it to %2F
        # and %2F can not be recognized in couchdb
        request = HTTPRequest(
            url="{0}/{1}".format(self.url, uri),
            method=method,
            headers={'Content-Type': 'application/json'},
            body=json_encode(body) if body else None
        )
        return self.client.fetch(request, **kwargs)

    @gen.coroutine
    def head(self, database, doc_id):
        uri = database + '/' + doc_id
        resp = yield self.fetch(uri, "HEAD")
        raise gen.Return(resp)

    @gen.coroutine
    def get(self, database, doc_id, **kwargs):
        uri = database + '/' + doc_id
        resp = yield self.fetch(uri, "GET", **kwargs)
        raise gen.Return(resp)

    @gen.coroutine
    def put(self, database, doc_id, doc):
        uri = database + '/' + doc_id
        resp = yield self.fetch(uri, "PUT", body=doc)
        raise gen.Return(resp)

    @gen.coroutine
    def delete(self, database, doc_id, rev):
        # url_escape turn '=' into '%3F'
        # '%3F' not work in couchdb
        req = HTTPRequest(
            url="{0}/{1}/{2}?rev={3}".format(
                self.url,
                database,
                doc_id,
                rev
            ),
            method="DELETE",
            headers={'Content-Type': 'application/json'}
        )
        resp = yield self.client.fetch(req)
        raise gen.Return(resp)
