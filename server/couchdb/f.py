#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import couchdb


class Service(object):
    doc = {"type": "service"}
    services = [
        2181,  # zookeeper
        3306,  # mysql
        8080,  # tomcat
        11211,  # memcache
        22201,  # memcacheq
        61616,  # activemq
    ]

    def __init__(self, couchdb):
        self.db = couchdb

    def get_all(self):
        res = []
        for _id in self.db:
            if not _id.startswith("_") and re.match(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:\d{1,3}', _id):
                res.append(_id)
        return res

    def add(self, ip, port, **kwargs):
        _id = "{0}:{1}".format(ip, port)
        if port not in self.services:
            raise ValueError('need argument name=service_name')
        doc = self.doc.copy()
        doc.update({"_id": _id, "ip": ip, "port": port})
        for key in kwargs:
            doc[key] = kwargs[key]
        return self.db.save(doc)

    def update(self, _id, **kwargs):
        doc = self.db[_id]
        for key in kwargs:
            doc[key] = kwargs[key]
        return self.db.save(doc)


class Project(object):
    doc = {"type": "project"}

    def __init__(self, couchdb):
        self.db = couchdb

    def __getitem__(self, _id):
        return self.db[_id]

    def add_project(self, project_name, services=None):
        _id = project_name
        doc = self.doc.copy()
        doc.update({"_id": _id, "services": services})
        return self.db.save(doc)

    def add_service(self, _id, service_id):
        pass

    def delete_service(self, _id, service_id):
        pass

if __name__ == '__main__':
    db = couchdb.Server("http://172.16.200.51:5984")["cmdb"]
    service = Service(db)
    project = Project(db)
    doc = project["用户中心"]