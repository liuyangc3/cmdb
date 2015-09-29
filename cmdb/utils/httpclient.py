#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado import gen
from tornado.httpclient import HTTPRequest
from tornado.httpclient import AsyncHTTPClient
from tornado.escape import url_escape, json_encode


class CouchAsyncHTTPClient(object):
    def __init__(self, url, io_loop):
        self.url = url
        self.io_loop = io_loop
        self.client = AsyncHTTPClient(self.io_loop)

    def _fetch(self, *args, **kwargs):
        return self.client.fetch(*args, **kwargs)

    def make_request(self, uri, method, doc=None):
        return HTTPRequest(
            url="{0}/{1}".format(self.url, url_escape(uri)),
            method=method,
            headers={'Content-Type': 'application/json'},
            body=json_encode(doc) if doc else None
        )

    @gen.coroutine
    def head(self, uri):
        resp = yield self._fetch(
            self.make_request(uri, "HEAD")
        )
        raise gen.Return(resp)

    @gen.coroutine
    def get(self, uri):
        resp = yield self._fetch(
            self.make_request(uri, "GET")
        )
        raise gen.Return(resp)

    @gen.coroutine
    def put(self, uri, doc):
        resp = yield self._fetch(
            self.make_request(uri, "PUT", doc=doc)
        )
        raise gen.Return(resp)

    @gen.coroutine
    def delete(self, uri, rev):
        uri += "?rev={0}".format(rev)
        resp = yield self._fetch(
            self.make_request(uri, "DELETE")
        )
        raise gen.Return(resp)
