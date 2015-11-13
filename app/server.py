#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import os
from tornado import httpserver
from tornado import ioloop
from tornado import web
from tornado.options import define, options


class Application(web.Application):
    def __init__(self):
        from app.route import router
        # extend plugins.handlers into tornado handlers
        # uri in plugins will be changed to '/plugins/module_name/uri'
        for root, _dir, plugins in os.walk(
                os.path.join(os.path.dirname(__file__), "plugins")
        ):
            plugins.remove("__init__.py")
            for plugin in plugins:
                if plugin.endswith('py'):
                    module_name = plugin.split('.')[0]
                    url_prefix = '/plugins/' + module_name   # /plugins/module_name
                    package = 'app.plugins.' + module_name  # app.plugins.module_name
                    module = __builtins__.__import__(package, fromlist=['app.plugins'])
                    for suffix, handler in module.handlers:
                        url = url_prefix + suffix
                        router.append((url, handler))

        settings = dict(
            # debug=True,
            static_path=os.path.join(os.path.dirname(__file__), "cmdb-front/app"),
            template_path=os.path.join(os.path.dirname(__file__), "cmdb-front/app/views"),
            cookie_secret="fgjiOJHhng&640",
            login_url="/login"
            # static_url_prefix=options.static_url_prefix,
        )
        super(Application, self).__init__(router, **settings)


def main():
    define("port", default=8005, help='run on the given port', type=int)
    options.parse_command_line()
    server = httpserver.HTTPServer(Application(), xheaders=True)
    server.listen(options.port)
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
