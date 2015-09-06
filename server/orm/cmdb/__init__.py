#!/usr/bin/python
# -*- coding: utf-8 -*-

from ..table import Service
from ..connector import session
from ..function import get_service_id, get_network_ip


def get_project_service(project_name, service_name):
    sid = get_service_id(service_name)
    result = session.query(
        Service.network_resource_id,
        Service.port
    ).filter_by(
        project_name=project_name,
        service_name_id=sid
    ).all()
    if result:
        res = []
        for nid, port in result:
            res.append({"ip": get_network_ip(nid), "port": port, "name": service_name})
        return res
    raise ValueError("invalid project name '%s'" % project_name)
