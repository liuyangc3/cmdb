#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from conf import MySQL


engine = create_engine("mysql://{0}:{1}@{2}".format(MySQL.user, MySQL.passwd, MySQL.url),
                       pool_size=MySQL.poll_size, pool_timeout=MySQL.pool_timeout,
                       max_overflow=MySQL.max_overflow, encoding="utf-8")

Session = sessionmaker(bind=engine)
session = Session()
