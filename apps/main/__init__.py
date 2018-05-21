#!/usr/bin/env python
# encoding: utf-8 
# @version: 
# @author: liduo
# @license: 
# @file: __init__.py.py
# @time: 2018/5/18 下午4:46
from flask import Blueprint

main = Blueprint("main", __name__)
import views

if __name__ == '__main__':
    pass
