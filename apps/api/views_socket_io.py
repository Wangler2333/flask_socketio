#!/usr/bin/env python
# encoding: utf-8 
# @version: 
# @author: liduo
# @license: 
# @file: socket.py
# @time: 2018/5/20 下午4:05
from apps import socket_io, redis_store, login_required
from flask import request, g
from flask.ext.socketio import emit,join_room,leave_room


@socket_io.on('connect', namespace='/')
@login_required
def connect():
    user_id = g.user_id
    sid = request.sid
    redis_store.set(user_id, sid)


@socket_io.on('disconnect', namespace='/')
@login_required
def disconnect():
    user_id = g.user_id
    redis_store.delete(user_id)
    print('Client disconnected')


@socket_io.on("chatMessage", namespace="/")
@login_required
def socket(data):
    print data
    print(request.namespace)
    print(request.event)


if __name__ == '__main__':
    pass
