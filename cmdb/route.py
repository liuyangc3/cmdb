#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from tornado.web import RedirectHandler
from tornado.web import StaticFileHandler
from cmdb.handlers import *

re_name = '([a-zA-Z0-9%]+)'
re_ip_port = '(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{2,5})'
static = os.path.dirname(__file__)

router = [
    (r'/', IndexHandler),

    # define static files
    (r'/js/(.*)', StaticFileHandler, {"path": os.path.join(static, "cmdb-front/app/js")}),
    (r'/css/(.*)', StaticFileHandler, {"path": os.path.join(static, "cmdb-front/app/css")}),
    (r'/views/(.*)', StaticFileHandler, {"path": os.path.join(static, "cmdb-front/app/views")}),
    (r'/image/(.*)', StaticFileHandler, {"path": os.path.join(static, "cmdb-front/app/image")}),


    # couch api
    (r'/api/v1/{0}/couch/list'.format(re_name), ServicesHanlder),
    (r'/api/v1/{0}/couch/search'.format(re_name), ServiceSearchHandler),
    (r'/api/v1/{0}/couch/{1}'.format(re_name, re_ip_port), ServiceHanlder),

    # project api
    (r'/api/v1/{0}/project/list'.format(re_name), ProjectsHandler),
    (r'/api/v1/{0}/project/search'.format(re_name), ProjectSearchHandler),
    (r'/api/v1/{0}/project/{1}'.format(re_name, re_ip_port), ProjectHandler),


    # 非api开头的请求 由前段框架处理
    (r'^/(?!api/v1/).+', RedirectHandler, {"base_url": "/"})
]
