from datetime import datetime

from sqlalchemy import Integer, Column, String, DateTime
from app.models.base import BaseCrud


class LogInterface(BaseCrud):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)
    # : log message
    # : 日志信息
    message = Column(String(450), comment="日志信息")
    # : create time
    # : 日志创建时间
    _time = Column('time', DateTime, default=datetime.now, comment="日志创建时间")
    # : user id
    # : 用户id
    user_id = Column(Integer, nullable=False, comment="用户id")
    # user_name at that moment
    # 用户当时的昵称
    user_name = Column(String(20), comment="用户当时的昵称")
    # : status_code check request is success or not
    # : 请求的http返回码
    status_code = Column(Integer, comment="请求的http返回码")
    # request method
    # 请求方法
    method = Column(String(20), comment="请求方法")
    # request path
    # 请求路径
    path = Column(String(50), comment="请求路径")
    # which authority is accessed
    # 访问哪个权限
    authority = Column(String(100), comment="访问哪个权限")

    @property
    def time(self):
        if self._time is None:
            return None
        return int(round(self._time.timestamp() * 1000))


"""
import re
from functools import wraps
from flask import Response, request

REG_XP = r'[{](.*?)[}]'
OBJECTS = ['user', 'response', 'request']



class Logger(object):
    # message template
    template = None

    def __init__(self, template=None):
        if template:
            self.template: str = template
        elif self.template is None:
            raise Exception('template must not be None!')
        self.message = ''
        self.response = None
        self.user = None


    # 解析自定义模板
    def _parse_template(self):
        message = self.template
        total = re.findall(REG_XP, message)
        for it in total:
            assert '.' in it, '%s中必须包含 . ,且为一个' % it
            i = it.rindex('.')
            obj = it[:i]
            assert obj in OBJECTS, '%s只能为user,response,request中的一个' % obj
            prop = it[i + 1:]
            if obj == 'user':
                item = getattr(self.user, prop, '')
            elif obj == 'response':
                item = getattr(self.response, prop, '')
            else:
                item = getattr(request, prop, '')
            message = message.replace('{%s}' % it, str(item))
        return message
"""