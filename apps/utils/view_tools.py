#!/usr/bin/env python
# encoding: utf-8 
# @version: 
# @author: liduo
# @license: 
# @file: model_tools.py
# @time: 2018/5/20 下午8:52
from apps import db
from apps.utils.response_code import RET
from flask import current_app, jsonify


def model_commit(model=None):
    try:
        if model:
            db.session.add(model)
        db.session.commit()
        return None
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(code=RET.DATAERR, msg="模型类保存错误")


class FormVal:
    def __init__(self, request):
        forms = request.form
        for key in forms:
            setattr(self, key, forms.get(key))


if __name__ == '__main__':
    pass
