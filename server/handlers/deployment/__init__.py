#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from tornado.web import RequestHandler
from orm.deployment import get_service_info


class DeploymentHandler(RequestHandler):
    def get(self, ip, port):
        self.write(json.dumps(
            get_service_info(ip, port)
        ))


class DeploymentDateHandler(RequestHandler):
    def get(self, ip, port):
        # zmq
        pass

