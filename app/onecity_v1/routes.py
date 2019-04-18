# -*- coding: utf-8 -*-

###
### DO NOT CHANGE THIS FILE
### 
### The code is auto generated, your change will be overwritten by 
### code generating.
###
from __future__ import absolute_import

from .api.register import Register
from .api.login import Login
from .api.user_information import UserInformation


routes = [
    dict(resource=Register, urls=['/register'], endpoint='register'),
    dict(resource=Login, urls=['/login'], endpoint='login'),
    dict(resource=UserInformation, urls=['/user/information'], endpoint='user_information'),
]