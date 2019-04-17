# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import request, g

from app.libs.error_code import Success, Failed, InvalidTokenException
from app.onecity_v1.decorators import response_filter, request_validate, api_logger
from app.services.user import UserService
from . import Resource


class Register(Resource):
    method_decorators = [request_validate, response_filter, api_logger]

    def post(self):
        print(g.json)
        user = UserService()
        data = user.post_user(g.json)
        return Success('用户创建成功')
