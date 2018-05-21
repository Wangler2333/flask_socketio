#!/usr/bin/env python
# encoding: utf-8 
# @version: 
# @author: liduo
# @license: 
# @file: __init__.py.py
# @time: 2018/5/18 下午4:43
import os
import redis
import logging

from flask import Flask, jsonify, session, g, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf.csrf import CSRFProtect
from flask.ext.mail import Mail
from flask.ext.session import Session
from flask.ext.socketio import SocketIO
from config import basedir
from logging.handlers import RotatingFileHandler
from werkzeug.routing import BaseConverter
from functools import wraps

db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()
socket_io = SocketIO()

redis_store = None

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler(os.path.join(basedir, "logs/log.log"), maxBytes=1024 * 1024 * 100,
                                       backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)


class ReConverter(BaseConverter):
    u"""自定义的支持传入正则表达式的转换器"""

    def __init__(self, url_map, *args):
        # args接收正则表达式
        super(ReConverter, self).__init__(url_map)
        self.regex = args[0]  # 接收正则表达式进行匹配

    def to_python(self, value):
        u"""从正则提取的参数，经过to_python处理后，返回给视图函数"""
        return value

    def to_url(self, value):
        u"""从python变量转换到url时被调用，例如url_for("index",id="123")"""
        return value


def login_required(view_func):
    u"""检验用户的登录状态"""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is not None:
            # 表示用户已经登录
            # 使用g对象保存user_id，在视图函数中可以直接使用
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 用户未登录
            resp = {
                "code": 4001,
                "msg": u"用户未登录"
            }
            return jsonify(resp)

    return wrapper


def create_app(config):
    app = Flask(__name__)  # type: Flask
    app.config.from_object(config)

    config.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    Session(app)
    socket_io.init_app(app)

    app.url_map.converters["re"] = ReConverter

    global redis_store
    redis_store = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB,
                                    password=config.REDIS_PASSWD)

    from apps.main import main
    from apps.api import api
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(main)

    return app


import models
