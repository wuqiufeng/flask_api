from sqlalchemy import Integer, Column, String

from app import db
from app.models.base import InfoCrud as Base


class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)

    # : log message
    # : 日志信息
    message = Column(String(450))
    # : create time
    # : 日志创建时间
    _time = Column('time', TIMESTAMP(True), default=datetime.now)
    # : user id
    # : 用户id
    user_id = Column(Integer, nullable=False)
    # user_name at that moment
    # 用户当时的昵称
    user_name = Column(String(20))
    # : status_code check request is success or not
    # : 请求的http返回码
    status_code = Column(Integer)
    # request method
    # 请求方法
    method = Column(String(20))
    # request path
    # 请求路径
    path = Column(String(50))

    @property
    def time(self):
        if self._time is None:
            return None
        return int(round(self._time.timestamp() * 1000))

    @staticmethod
    def create_log(**kwargs):
        log = Log()
        for key in kwargs.keys():
            if hasattr(log, key):
                setattr(log, key, kwargs[key])
        db.session.add(log)
        if kwargs.get('commit') is True:
            db.session.commit()
        return log


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

    """
    def __call__(self, func):
        @wraps(func)
        def wrap(*args, **kwargs):
            response: Response = func(*args, **kwargs)
            self.response = response
            self.user = get_current_user()
            self.message = self._parse_template()
            self.write_log()
            return response

        return wrap


    def write_log(self):
        info = find_info_by_ep(request.endpoint)
        authority = info.auth if info is not None else ''
        status_code = getattr(self.response, 'status_code', None)
        if status_code is None:
            status_code = getattr(self.response, 'code', None)
        if status_code is None:
            status_code = 0
        Log.create_log(message=self.message, user_id=self.user.id, user_name=self.user.nickname,
                       status_code=status_code, method=request.method,
                       path=request.path, authority=authority, commit=True)
"""


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
