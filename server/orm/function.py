#!/usr/bin/python
# -*- coding: utf-8 -*-

from orm.table import Service, ServiceName, Network
from orm.connector import session


def get_service_id_from_name(service_name):
    return session.query(ServiceName.id).filter_by(sname=service_name)[0][0]


def get_service_name(sid):
    return session.query(ServiceName.sname).filter_by(id=sid)[0][0]


def get_network_id(ip):
    return session.query(Network.id).filter_by(ip=ip)[0][0]


def get_netword_ip(id):
    return session.query(Network.ip).filter_by(id=id)[0][0]
