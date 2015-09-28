#!/usr/bin/python
# -*- coding: utf-8 -*-

from tornado.web import RequestHandler


class DeploymnetBase(RequestHandler):
    def initialize(self):
        import zerorpc
        self._rpc_clinet = zerorpc.Client()


class DeploymentHandler(DeploymnetBase):
    pass


handlers = [
    (r'/my_url', DeploymentHandler)
]
