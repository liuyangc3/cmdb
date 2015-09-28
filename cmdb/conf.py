#!/usr/bin/python
# -*- coding: utf-8 -*-


class CouchdbConf:
    url = "http://127.0.0.1:5984/"
    database = "cmdb"

service_map = {
        "2181": "zookeeper",
        "3306": "mysql",
        "8080": "tomcat",
        "11211": "memcache",
        "22201": "memcacheq",
        "61616": "activemq"
    }



