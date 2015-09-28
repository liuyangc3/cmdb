#!/usr/bin/python
# -*- coding: utf-8 -*-

from cmdb.handlers.cmdbHandlers import *

re_project_name = '[a-zA-z0-9%]+'
re_ip_port = '\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{2,5}'

handlers = [
    (r'/api/v1/service/_list', ServiceHanlder),
    (r'/api/v1/service/({0})'.format(re_ip_port), ServiceRegexpHanlder),

    (r'/api/v1/project/({0})'.format(re_project_name), ProjectHandler)

    # /api/v1/deployment/search/(ip)/(port)/deploymentDate
]
