#!/usr/bin/env python
# encoding: utf-8 
# @version: 
# @author: liduo
# @license: 
# @file: __init__.py.py
# @time: 2018/5/18 下午10:08
from flask import Blueprint

api = Blueprint("api", __name__)
import views, views_socket_io

if __name__ == '__main__':
    pass
