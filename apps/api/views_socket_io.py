#!/usr/bin/env python
# encoding: utf-8 
# @version: 
# @author: liduo
# @license: 
# @file: socket.py
# @time: 2018/5/20 下午4:05
from apps import socket_io, redis_store, login_required
from flask import request, g, session
from flask.ext.socketio import emit, join_room, leave_room
import time


@socket_io.on('connect', namespace='/')
def connect():
    user_id = session.get("user_id")
    if user_id is None:
        return False
    sid = request.sid
    redis_store.set(user_id, sid)


@socket_io.on('disconnect', namespace='/')
def disconnect():
    user_id = session.get("user_id")
    if user_id is None:
        return False
    redis_store.delete(user_id)
    print('Client disconnected')


@socket_io.on("chatMessage", namespace="/")
def socket(data):
    data_mine = data["data"].get("mine")
    data_to = data["data"].get("to")

    # 消息来源
    data_mine_id = data_mine.get("id")  # 我的id
    data_mine_username = data_mine.get("username")  # 我的昵称
    data_mine_avatar = data_mine.get("avatar")  # 我的头像
    data_mine_mine = data_mine.get("mine")  # 是否是我发送的消息
    data_mine_content = data_mine.get("content")  # 消息内容

    # 消息目标
    data_to_id = data_to.get("id")  # 目标id
    data_to_username = data_to.get("username")  # 目标昵称
    data_to_avatar = data_to.get("avatar")  # 目标头像
    data_to_type = data_to.get("type")  # 目标类型：friend，group
    data_to_name = data_to.get("name")  # 目标姓名
    data_to_sign = data_to.get("sign")  # 上一次打开聊天框时发送的最后一条消息
    data_to_content = data_to.get("content")  # 上一次打开聊天框时发送的最后一条消息
    data_to_historyTime = data_to.get("historyTime")  # 打开对话框的时间

    data_timestamp = time.time() * 1000

    if data_mine_mine:
        to_sid = redis_store.get(data_to_id)
        data = {"username": data_mine_username, "avatar": data_mine_avatar, "id": data_mine_id, "type": data_to_type,
                "content": data_mine_content, "mine": data_mine_mine, "timestamp": data_timestamp}
        # emit("chatMessage", data, room=to_sid)
        emit("chatMessage", data, broadcast=True)


if __name__ == '__main__':
    pass
