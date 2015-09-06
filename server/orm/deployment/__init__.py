#!/usr/bin/python
# -*- coding: utf-8 -*-

from ..table import Service
from ..connector import session
from ..function import get_network_id, get_service_name


def get_service_info(ip, port):
    nid = get_network_id(ip)
    result = session.query(Service.service_name_id).filter_by(
        port=port,
        network_resource_id=nid
    ).first()
    if result:
        return {"ip": ip, "port": port, "name": get_service_name(result[0])}
    raise ValueError("invalid port '%s'" % port)

