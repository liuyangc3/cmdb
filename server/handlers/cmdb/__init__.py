#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from tornado.web import RequestHandler

from orm.cmdb import get_project_service


class ServiceHandler(RequestHandler):
    def get(self, project_name, service_name):
        self.write(
            json.dumps(get_project_service(project_name, service_name))
        )
