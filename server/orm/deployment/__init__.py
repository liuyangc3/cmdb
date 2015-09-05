#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'web'

from orm.table import Service
from orm.connector import session
from orm.function import get_network_id, get_service_name


def get_service_info(ip, port):
    nid = get_network_id(ip)
    res = {}
    try:
        sid = session.query(Service.service_name_id).filter_by(
            port=port,
            network_resource_id=nid
        )[0][0]
        sname = get_service_name(sid)
        res["ip"] = ip
        res["port"] = port
        res["name"] = sname
        return res
    except IndexError, e:
        return None

