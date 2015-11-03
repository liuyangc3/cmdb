#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from tornado.web import RedirectHandler
from tornado.web import StaticFileHandler
from cmdb.handlers import *

# must begin with a letter
# only lowercase characters, digits, and '-_'
re_db_name = '([a-z][a-z0-9-_]+)'
re_service_name = '(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{2,5})'
re_project_name = '([a-zA-Z0-9%]+)'

static = os.path.dirname(__file__)

router = [
    (r'/', IndexHandler),

    # define static files
    (r'/js/(.*)', StaticFileHandler, {"path": os.path.join(static, "cmdb-front/app/js")}),
    (r'/css/(.*)', StaticFileHandler, {"path": os.path.join(static, "cmdb-front/app/css")}),
    (r'/views/(.*)', StaticFileHandler, {"path": os.path.join(static, "cmdb-front/app/views")}),
    (r'/image/(.*)', StaticFileHandler, {"path": os.path.join(static, "cmdb-front/app/image")}),

    # database api
    (r'/api/v1/database/list'.format(re_db_name), DatabasesHandler),
    (r'/api/v1/database/{0}'.format(re_db_name), DatabaseHandler),

    # service api
    (r'/api/v1/{0}/service/list'.format(re_db_name), ServicesHanlder),

    (r'/api/v1/{0}/service/{1}'.format(re_db_name, re_service_name), ServiceHanlder),

    # project api
    (r'/api/v1/{0}/project/list'.format(re_db_name), ProjectsHandler),
    (r'/api/v1/{0}/project/{1}'.format(re_db_name, re_project_name), ProjectHandler),

    # search api
    (r'/api/v1/{0}/search'.format(re_db_name), SearchHandler),

    # 非api开头的请求 由前段框架处理
    (r'^/(?!api/v1/).+', RedirectHandler, {"url": "/"})
]
