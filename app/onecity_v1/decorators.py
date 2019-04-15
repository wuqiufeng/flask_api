# -*- coding: utf-8 -*-
from functools import wraps
from http.client import HTTPException

import six
from flask import current_app, request, json, g
from flask_restful import unpack, abort

from app.libs.error_code import AuthFailed, APIException
from app.onecity_v1.schemas import filters, normalize, resolver
from app.onecity_v1.validators import JSONEncoder


class Token():
    def __init__(self, token_value):
        self.value = token_value




def response_filter(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        resp = view(*args, **kwargs)

        if isinstance(resp, current_app.response_class):
            return resp

        endpoint = request.endpoint.partition('.')[-1]
        method = request.method
        if method == 'HEAD':
            method = 'GET'
        filter = filters.get((endpoint, method), None)
        if not filter:
            return resp

        headers = None
        status = None
        if isinstance(resp, tuple):
            resp, status, headers = unpack(resp)

        if len(filter) == 1:
            if six.PY3:
                status = list(filter.keys())[0]
            else:
                status = filter.keys()[0]

        schemas = filter.get(status)
        if not schemas:
            return resp, status, headers
            # abort(500, message='`%d` is not a defined status code.' % status)

        resp, errors = normalize(schemas['schema'], resp, resolver=resolver)
        if schemas['headers']:
            headers, header_errors = normalize(
                {'properties': schemas['headers']}, headers, resolver=resolver)
            errors.extend(header_errors)
        if errors:
            abort(500, message='Expectation Failed', errors=errors)

        return current_app.response_class(
            json.dumps(resp, cls=JSONEncoder) + '\n',
            status=status,
            headers=headers,
            mimetype='application/json'
        )

    return wrapper



def api_logger(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        try:
            if "X-API-TOKEN" in request.headers:
                setattr(g, "token", Token(request.headers["X-API-TOKEN"]))
            # service_logger.info(_request_log(request))
            return view(*args, **kwargs)
        except HTTPException as h:
            # service_logger.warning("<Response [{}]>".format(h))
            raise h
        except Exception as e:
        #     service_logger.critical("<Response [500 Internal Server Error]>")
        #     error_logger.error(_request_log(request))
        #     error_logger.error(e, exc_info=True)
            raise e

    return wrapper


# Decorator for API authentication
def authentication(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not hasattr(g, "token"):
            raise AuthFailed("Token not found")

        if g.token.value != 'aabbcc':
            raise AuthFailed("您的身份认证已经失效， 请重新登录")

        # if g.token.value != redis_client.get("token:{}".format(g.token.name)):
        #     raise AuthFailed("您的身份认证已经失效， 请重新登录")
        return view(*args, **kwargs)

    return wrapper