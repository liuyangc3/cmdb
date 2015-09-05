#!/usr/bin/python
# -*- coding: utf-8 -*-

from handlers.cmdb import ServiceHandler
from handlers.deployment import DeploymentHandler, DeploymentDateHandler

re_project_name = '[a-zA-z0-9%]+'
re_ip = '\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}'

handlers = [
    # /api/v1/(project_name)/(service_name)
    (r'/api/v1/(%s)/(\w+)' % re_project_name,
     ServiceHandler),

    # /api/v1/service/(ip)/(port)
    (r'/api/v1/service/(%s)/(\d+)' % re_ip,
     DeploymentHandler),

    # /api/v1/service/(ip)/(port)/deploymentDate
    (r'/api/v1/service/(%s)/(\d+)/deploymentDate' % re_ip,
     DeploymentDateHandler),
]
