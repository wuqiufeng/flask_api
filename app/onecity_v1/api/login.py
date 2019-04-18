# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from flask import request, g

from app.onecity_v1.decorators import request_validate, response_filter, api_logger
from app.services.user import UserService
from . import Resource
from .. import schemas


class Login(Resource):
    method_decorators = [request_validate, response_filter, api_logger]

    def post(self):
        print(g.json)
        user = UserService()
        data = user.login(g.json)
        data = dict(
            error_code=0,
            msg='ok',
            data=data
        )
        return data, 200, None
