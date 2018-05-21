#!/usr/bin/env python
# encoding: utf-8 
# @version: 
# @author: liduo
# @license: 
# @file: views.py
# @time: 2018/5/18 下午5:16
from apps import redis_store
from apps.main import main
from flask import current_app, make_response, request
from flask_wtf.csrf import generate_csrf


@main.route("/get/image")
def get_image():
    image_code = request.args.get("code")
    image_code = "image_" + image_code
    image = redis_store.get(image_code)

    # 返回验证码图片
    resp = make_response(image)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


@main.route("/<re('.*'):name>", methods=["GET"])
def index(name):
    if not name:
        name = "index.html"

    csrf_token = generate_csrf()
    res = make_response(current_app.send_static_file(name))
    res.set_cookie("csrf_token", csrf_token)
    return res


if __name__ == '__main__':
    pass
