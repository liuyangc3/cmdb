#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="cmdb",
    version="0.1",
    description="cmdb backend",
    author="liuyang",
    install_requires=[
        "tornado>=4.0", 'mock',
    ]
)
