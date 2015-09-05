#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'web'

from orm.table import Service
from orm.connector import session
from orm.function import get_service_id_from_name, get_netword_ip


def get_project_service(project_name, service_name):

    try:
        sid = get_service_id_from_name(service_name)
    except Exception, e:
        return None
    try:
        res = []
        for nid, port in session.query(
                Service.network_resource_id,
                Service.port
        ).filter_by(
            project_name=project_name,
            service_name_id=sid
        ):
            res.append({"ip": get_netword_ip(nid), "port": port, "name": service_name})
        if not res:
            return None
        return res
    except Exception, e:
        return None
