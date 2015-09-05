#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'web'

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Network(Base):
    __tablename__ = 'network_resource'
    id = Column(Integer, primary_key=True)
    ip = Column('intra_ip', String(19))


class ServiceName(Base):
    __tablename__ = 'service_name'
    id = Column(Integer, primary_key=True)
    sname = Column(String(20))


class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    network_resource_id = Column(Integer)
    service_name_id = Column(Integer)
    project_name = Column(String(45))
    port = Column(String(6))

    def __repr__(self):
        return "<Service(id={0}, network_resource_id={1}, service_name_id={2}, project_name={3})>" \
            .format(self.id, self.network_resource_id, self.service_name_id, self.project_name)