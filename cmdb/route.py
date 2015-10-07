#!/usr/bin/python
# -*- coding: utf-8 -*-

from tornado.web import RedirectHandler

from cmdb.handlers import *

re_project_name = '[A-Z0-9%]+'
re_ip_port = '\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{2,5}'

router = [
    # service api
    (r'/api/v1/service/list', ServicesHanlder),
    (r'/api/v1/service/({0})'.format(re_ip_port), ServiceHanlder),
    # project api
    (r'/api/v1/project/list', ProjectsHandler),
    (r'/api/v1/project/({0})'.format(re_project_name), ProjectHandler),
    # 非api开头的请求 由前段框架处理
    (r'^/(?!api/v1/).+', RedirectHandler, {"url": "/"})
]
