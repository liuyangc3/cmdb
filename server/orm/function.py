#!/usr/bin/python
# -*- coding: utf-8 -*-

from .table import ServiceName, Network
from .connector import session


def get_service_id(service_name):
    result = session.query(ServiceName.id).filter_by(sname=service_name).first()
    if result:
        return result[0]
    raise ValueError("invalid service name '%s'" % service_name)


def get_network_id(ip):
    result = session.query(Network.id).filter_by(ip=ip).first()
    if result:
        return result[0]
    raise ValueError("invalid ip address '%s'" % ip)


def get_service_name(sid):
    return session.query(ServiceName.sname).filter_by(id=sid)[0][0]


def get_network_ip(id):
    return session.query(Network.ip).filter_by(id=id)[0][0]
