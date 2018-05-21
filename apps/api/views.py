#!/usr/bin/env python
# encoding: utf-8 
# @version: 
# @author: liduo
# @license: 
# @file: views.py
# @time: 2018/5/18 下午10:08
from flask import current_app, jsonify, request, session, make_response
from apps import csrf, login_required, redis_store, constants
from apps.utils.response_code import RET
from apps.utils.captcha.captcha import captcha
from apps.models import UserInfo
from apps.api import api
from apps.utils.view_tools import model_commit
import random
import uuid
import re


@api.route("/login", methods=["POST"])
def login():
    val_username = request.form.get("username")
    val_password = request.form.get("password")
    val_vercode = request.form.get("vercode")
    val_image_code = request.form.get("image_code")
    val_access_token = request.form.get("access_token")
    val_remember = request.form.get("remember")

    # 校验参数
    if not all([val_username, val_password, val_vercode, val_image_code]):
        return jsonify(code=RET.PARAMERR, msg="参数不完整")

    # 判断手机号格式
    if not re.match(r"1[34578]\d{9}", val_username):
        return jsonify(code=RET.DATAERR, msg="手机号格式错误")

    # 业务逻辑
    try:
        redis_image_code = redis_store.get("image_code_%s" % val_image_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg="查询图片验证码错误")

    if redis_image_code is None:
        return jsonify(code=RET.NODATA, msg="图片验证码过期")

    if val_vercode.lower() != redis_image_code.lower():
        return jsonify(code=RET.DATAERR, msg="图片验证码错误")

    user = UserInfo.query.filter_by(phone=val_username).first()
    if user is None:
        return jsonify(code=RET.DATAERR, msg="账号或密码错误")

    if not user.check_password(val_password):
        return jsonify(code=RET.DATAERR, msg="账号或密码错误")

    # 利用session记录用户的登录状态

    access_token = str(uuid.uuid3(uuid.NAMESPACE_URL, str(val_username)))

    session["user_id"] = user.id
    session["user_name"] = val_username
    session["access_token"] = access_token

    resp = {
        "code": RET.OK,
        "msg": "登陆成功",
        "data": {
            "access_token": access_token
        }
    }
    # 删除验证码
    try:
        redis_store.delete("image_code_%s" % val_username)
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(resp)


@api.route("/register", methods=["POST"])
def register():
    print(request.form)
    val_cellphone = request.form.get("cellphone")
    val_password = request.form.get("password")
    val_repass = request.form.get("repass")
    val_vercode = request.form.get("vercode")
    val_nickname = request.form.get("nickname")
    val_agreement = request.form.get("agreement")

    # 校验参数
    if not all([val_cellphone, val_vercode, val_password, val_repass, val_nickname, val_agreement]):
        return jsonify(code=RET.PARAMERR, msg="参数不完整")

    # 判断手机号格式
    if not re.match(r"1[345789]\d{9}", val_cellphone):
        return jsonify(code=RET.DATAERR, msg="手机号格式错误")

    if val_password != val_repass:
        return jsonify(code=RET.DATAERR, msg="两次密码不同")

    # 业务逻辑
    # 获取真实的短信验证码
    try:
        real_sms_code = redis_store.get("sms_code_%s" % val_cellphone)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg="查询短信验证码错误")

    # 判断短信验证码是否过期
    if real_sms_code is None:
        return jsonify(code=RET.NODATA, msg="短信验证码过期")

    # 对于用户输入的短信验证码是否正确
    if real_sms_code != val_vercode:
        return jsonify(code=RET.DATAERR, msg="短信验证码错误")

    # 删除短信验证码
    try:
        redis_store.delete("sms_code_%s" % val_cellphone)
    except Exception as e:
        current_app.logger.error(e)

    # 保存用户的数据到数据库中
    user = UserInfo(username=val_nickname, phone=val_cellphone)
    # 对于password属性的设置，会调用属性方法，进行加密操作
    user.password = val_password

    resp = model_commit(user)
    if resp:
        return jsonify(code=RET.DATAEXIST, msg="用户手机号已经注册")

    if val_agreement != "on":
        return jsonify(code=RET.DATAEXIST, msg="请同意协议")

    # 返回值
    resp = {
        "code": RET.OK,
        "msg": "注册成功"
    }
    return jsonify(resp)


@api.route("/upload/<type>", methods=["POST"])
def upload(type):
    pass


@api.route("/main", methods=["POST"])
@login_required
def main():
    init = {
        "mine": {
            "username": "纸飞机", "id": 123,
            "avatar": "http://tvax1.sinaimg.cn/crop.0.0.300.300.180/006Iv8Wjly8ff7ghbigcij308c08ct8i.jpg",
            "sign": "懒得签名"
        },
        "friend": [
            {
                "groupname": "前端码屌",
                "id": 1,
                "online": 2,
                "list": [
                    {
                        "username": "贤心",
                        "id": "100001",
                        "avatar": "http://tp1.sinaimg.cn/1571889140/180/40030060651/1",
                        "sign": "这些都是测试数据，实际使用请严格按照该格式返回"
                    },
                    {
                        "username": "Z_子晴",
                        "id": "108101",
                        "avatar": "http://tva3.sinaimg.cn/crop.0.0.512.512.180/8693225ajw8f2rt20ptykj20e80e8weu.jpg",
                        "sign": "微电商达人"
                    },
                    {
                        "username": "Lemon_CC",
                        "id": "102101",
                        "avatar": "http://tp2.sinaimg.cn/1833062053/180/5643591594/0",
                        "sign": ""
                    },
                    {
                        "username": "马小云",
                        "id": "168168",
                        "avatar": "http://tp4.sinaimg.cn/2145291155/180/5601307179/1",
                        "sign": "让天下没有难写的代码",
                        "status": "offline"
                    },
                    {
                        "username": "徐小峥",
                        "id": "666666",
                        "avatar": "http://tp2.sinaimg.cn/1783286485/180/5677568891/1",
                        "sign": "代码在囧途，也要写到底"
                    }
                ]
            },
            {
                "groupname": "网红",
                "id": 2,
                "online": 3,
                "list": [
                    {
                        "username": "罗玉凤",
                        "id": "121286",
                        "avatar": "http://tp1.sinaimg.cn/1241679004/180/5743814375/0",
                        "sign": "在自己实力不济的时候，不要去相信什么媒体和记者。他们不是善良的人，有时候候他们的采访对当事人而言就是陷阱"
                    },
                    {
                        "username": "长泽梓Azusa",
                        "id": "100001222",
                        "sign": "我是日本女艺人长泽あずさ",
                        "avatar": "http://tva1.sinaimg.cn/crop.0.0.180.180.180/86b15b6cjw1e8qgp5bmzyj2050050aa8.jpg"
                    },
                    {
                        "username": "大鱼_MsYuyu",
                        "id": "12123454",
                        "avatar": "http://tp1.sinaimg.cn/5286730964/50/5745125631/0",
                        "sign": "我瘋了！這也太準了吧  超級笑點低"
                    },
                    {
                        "username": "谢楠",
                        "id": "10034001",
                        "avatar": "http://tp4.sinaimg.cn/1665074831/180/5617130952/0",
                        "sign": ""
                    },
                    {
                        "username": "柏雪近在它香",
                        "id": "3435343",
                        "avatar": "http://tp2.sinaimg.cn/2518326245/180/5636099025/0",
                        "sign": ""
                    }
                ]
            },
            {
                "groupname": "我心中的女神",
                "id": 3,
                "online": 1,
                "list": [
                    {
                        "username": "林心如",
                        "id": "76543",
                        "avatar": "http://tp3.sinaimg.cn/1223762662/180/5741707953/0",
                        "sign": "我爱贤心"
                    },
                    {
                        "username": "佟丽娅",
                        "id": "4803920",
                        "avatar": "http://tp4.sinaimg.cn/1345566427/180/5730976522/0",
                        "sign": "我也爱贤心吖吖啊"
                    }
                ]
            }],
        "group": [
            {
                "groupname": "前端群",
                "id": "101",
                "avatar": "http://tp2.sinaimg.cn/2211874245/180/40050524279/0"
            },
            {
                "groupname": "Fly社区官方群",
                "id": "102",
                "avatar": "http://tp2.sinaimg.cn/5488749285/50/5719808192/1"
            }
        ]
    }
    return jsonify(init)


@api.route("/getmembers", methods=["GET"])
def getmembers():
    pass


@api.route("/image")
def get_image_code():
    """提供图片验证码"""
    # 业务处理
    # 生成验证码图片
    # 名字, 验证码真实值，图片的二进制内容
    name, text, image_data = captcha.generate_captcha()

    image_code = str(uuid.uuid3(uuid.NAMESPACE_URL, str(name)))

    try:
        # 保存验证码的真实值与编号
        # redis_store.set("image_code_%s" % image_code_id, text)
        # redis_store.expires("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES)
        # 设置redis的数据与有效期
        redis_store.setex("image_code_%s" % image_code, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        redis_store.setex("image_%s" % image_code, constants.IMAGE_CODE_REDIS_EXPIRES, image_data)
    except Exception as e:
        # 在日志中记录异常
        current_app.logger.error(e)
        resp = {
            "code": RET.DBERR,
            # "errmsg": "save image code failed"
            "msg": "保存验证码失败"

        }
        return jsonify(resp)

    # # 返回验证码图片
    # resp = make_response(image_data)
    # resp.headers["Content-Type"] = "image/jpg"
    return jsonify(code=RET.OK, msg="生成图片成功",
                   data={"image_url": "/get/image?code=%s" % image_code, "image_code": image_code})


@api.route("/sms", methods=["POST"])
def sms():
    val_vercode = request.form.get("vercode")
    val_phone = request.form.get("phone")
    val_uuid = request.form.get("uuid")

    # 校验参数
    if not all([val_uuid, val_vercode, val_phone]):
        return jsonify(code=RET.PARAMERR, msg="参数不完整")

    # 业务处理
    # 取出真实的图片验证码
    try:
        real_image_code = redis_store.get("image_code_%s" % val_uuid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg="获取图片验证码失败")

    # 判断验证码的有效期
    if real_image_code is None:
        # 表示redis中没有这个数据
        return jsonify(code=RET.NODATA, msg="图片验证码过期")

    # 判断用户填写的验证码与真实的验证码
    if real_image_code.lower() != val_vercode.lower():
        # 表示用户填写错误
        return jsonify(code=RET.DATAERR, msg="图片验证码有误")

    # 判断用户手机号是否注册过
    try:
        user = UserInfo.query.filter_by(phone=val_phone).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            # 用户已经注册过
            return jsonify(code=RET.DATAEXIST, msg="用户手机号已经注册过")

    # 创建短信验证码
    sms_code = "%06d" % random.randint(0, 999999)

    # 保存短信验证码
    try:
        redis_store.setex("sms_code_%s" % val_phone, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg="保存短信验证码异常")

    # 发送验证码短信
    # try:
    #     ccp = CCP()
    #     result = ccp.send_template_sms(val_phone, [sms_code, str(constants.SMS_CODE_REDIS_EXPIRES / 60)], 1)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(code=RET.THIRDERR, msg="发送短信异常")
    result = 0

    if result == 0:
        # 发送成功
        # 删除redis中的图片验证码
        try:
            redis_store.delete("image_code_%s" % val_uuid)
        except Exception as e:
            current_app.logger.error(e)

        # return jsonify(code=RET.OK, msg="发送短信成功")
        return jsonify(code=RET.OK, msg="发送短信成功", data={"code": sms_code})
    else:
        return jsonify(code=RET.THIRDERR, msg="发送短信失败")


if __name__ == '__main__':
    pass
