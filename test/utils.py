#!/usr/bin/python
# -*- coding: utf-8 -*-

import cStringIO as StringIO
from tornado.concurrent import Future
from tornado.httpclient import HTTPRequest, HTTPResponse


def setup_fetch(mock_fetch, status_code, body=None):
    def side_effect(request, **kwargs):
        if request is not HTTPRequest:
            request = HTTPRequest(request)
        _buffer = StringIO.StringIO(body) if body else body
        # header = HTTPHeaders(headers)
        response = HTTPResponse(request, status_code, None, body)
        future = Future()
        future.set_result(response)
        return future

    mock_fetch.side_effect = side_effect


def setup_func(mock_func, returns=None):
    def side_effect(*args, **kwargs):
        future = Future()
        future.set_result(returns)
        return future
    mock_func.side_effect = side_effect