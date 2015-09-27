#!/usr/bin/python
# -*- coding: utf-8 -*-

from cmdb.handlers.cmdbHandlers import *
from cmdb.handlers.deployHandlers import *

re_project_name = '[a-zA-z0-9%]+'
re_ip_port = '\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{2,5}'

handlers = [
    (r'/', H),
    (r'/service/_list', ServiceHanlder),
    (r'/service/({0})'.format(re_ip_port), ServiceRegexpHanlder),

    # # /api/v1/(project_name)/(service_name)
    # (r'/api/v1/(%s)/(\w+)' % re_project_name,
    #  ProjectHandler),
    #
    # # /api/v1/service/(service_name)
    # (r'/api/v1/service/(\w+)', ServicesHandler),
    #
    # # /api/v1/service/search/(ip)/(port)
    # (r'/api/v1/service/search/(%s)/(\d+)' % re_ip,
    #  ServiceHandler),

    # /api/v1/deployment/search/(ip)/(port)/deploymentDate
    (r'/api/v1/deployment/search/(%s)/(\d+)/deploymentDate' % re_ip_port,
     DeploymentDateHandler),


]
