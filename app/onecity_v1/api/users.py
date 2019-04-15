# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import request, g

from app.libs.error_code import Success, Failed
from . import Resource
from .. import schemas


class Users(Resource):

    def get(self):
        data = {'name': '副红烛'}
        # raise Failed()
        raise Failed()
        # return {'error_code': 0, 'data': data, 'msg': '获取列表成功'}, 400, None

    def post(self):


        return None, 200, None