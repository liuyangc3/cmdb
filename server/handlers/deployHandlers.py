#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import json
from tornado.web import RequestHandler


class DeploymnetBase(RequestHandler):
    def initialize(self):
        import zerorpc
        self._rpc_clinet = zerorpc.Client()


class DeploymentDateHandler(DeploymnetBase):
    def get(self, ip, port):
        # check service exists
        # try:
        #     get_service_info(ip, port)
        #
        # except ValueError as e:
        #     self.write(e.message)

        try:
            self._rpc_clinet.connect("tcp://{0}:4242".format(ip))
            self.write(json.dumps(
                self._rpc_clinet.sorted_date_list()
            ))
            self.finish(self._rpc_clinet.close())
        except Exception as e:
            self.set_status(400)
            self.write(e.message)
            self.finish(self._rpc_clinet.close())