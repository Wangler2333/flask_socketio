#!/usr/bin/env python
# encoding: utf-8 
# @version: 
# @author: liduo
# @license: 
# @file: models.py
# @time: 2018/5/18 下午9:26
from apps import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""
    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


class UserInfo(BaseModel, db.Model):
    __tablename__ = "s_user_info"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    phone = db.Column(db.String(30), unique=True)
    password_hash = db.Column(db.String(30))
    avatar = db.Column(db.String(100), nullable=True)
    sign = db.Column(db.String(30), nullable=True)
    user_group = db.relationship("UserGroup", backref=db.backref("s_user_info"))
    group_friend = db.relationship("GroupFriend", backref=db.backref("s_user_info"))
    group_user = db.relationship("GroupUserRelation", backref=db.backref("s_user_info"))
    chat_info = db.relationship("ChatInfo", backref=db.backref("s_user_info"))
    chat_user = db.relationship("ChatUserRelation", backref=db.backref("s_user_info"))
    image = db.relationship("Image", backref=db.backref("s_user_info"))
    file = db.relationship("File", backref=db.backref("s_user_info"))

    @property
    def password(self):
        """对应password属性的读取操作"""
        raise AttributeError("不支持读取操作")

    @password.setter
    def password(self, value):
        """对应password属性的设置操作, value用户设置的密码值"""
        self.password_hash = generate_password_hash(value)

    def check_password(self, value):
        """检查用户密码， value 是用户填写密码"""
        return check_password_hash(self.password_hash, value)


class UserGroup(BaseModel, db.Model):
    __tablename__ = "s_user_group"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("s_user_info.id"))
    group_name = db.Column(db.String(30))
    group_friend = db.relationship("GroupFriend", backref=db.backref("s_user_group"))


class GroupFriend(BaseModel, db.Model):
    __tablename__ = "s_group_friend"
    id = db.Column(db.Integer, primary_key=True)
    user_group_id = db.Column(db.Integer, db.ForeignKey("s_user_group.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("s_user_info.id"))


class GroupInfo(BaseModel, db.Model):
    __tablename__ = "s_group_info"
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(30))
    avatar = db.Column(db.String(100), nullable=True)
    group_user = db.relationship("GroupUserRelation", backref=db.backref("s_group_info"))


class GroupUserRelation(BaseModel, db.Model):
    __tablename__ = "s_group_user"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("s_user_info.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("s_group_info.id"))


class ChatInfo(BaseModel, db.Model):
    __tablename__ = "s_chat_info"
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey("s_user_info.id"))
    chat_info = db.Column(db.Text)
    chat_user = db.relationship("ChatUserRelation", backref=db.backref("s_chat_info"))


class ChatUserRelation(BaseModel, db.Model):
    __tablename__ = "s_chat_user"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("s_user_info.id"))
    chat_id = db.Column(db.Integer, db.ForeignKey("s_chat_info.id"))
    is_read = db.Column(db.Boolean, default=False)


class Image(BaseModel, db.Model):
    __tablename__ = "s_image"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("s_user_info.id"))
    image_name = db.Column(db.String(30))
    image_url = db.Column(db.String(100))


class File(BaseModel, db.Model):
    __tablename__ = "s_file"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("s_user_info.id"))
    file_name = db.Column(db.String(30))
    file_url = db.Column(db.String(100))


if __name__ == '__main__':
    pass
