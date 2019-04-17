# -*- coding: utf-8 -*-
from functools import wraps
from http.client import HTTPException

import six
from flask import current_app, request, json, g
from flask_restful import unpack, abort
from werkzeug.datastructures import MultiDict

from app import service_logger, error_logger
from app.libs.error_code import AuthFailed, APIException, UnknownException, UnprocessableException
from app.onecity_v1.schemas import filters, normalize, resolver, scopes, validators, security
from app.onecity_v1.validators import JSONEncoder, FlaskValidatorAdaptor


class Token():
    def __init__(self, token_value):
        self.value = token_value


def request_validate(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        endpoint = request.endpoint.partition('.')[-1]
        # scope
        if (endpoint, request.method) in scopes and not set(
                scopes[(endpoint, request.method)]).issubset(set(security.scopes)):
            abort(403)
        # data
        method = request.method
        if method == 'HEAD':
            method = 'GET'
        locations = validators.get((endpoint, method), {})
        for location, schema in six.iteritems(locations):
            value = getattr(request, location, MultiDict())
            if value is None:
                value = MultiDict()
            validator = FlaskValidatorAdaptor(schema)
            result, errors = validator.validate(value)
            if errors:
                error_logger.error(_request_log(request))
                raise UnprocessableException()
            setattr(g, location, result)
        return view(*args, **kwargs)

    return wrapper


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
            print('try')
            service_logger.info(_request_log(request))
            return view(*args, **kwargs)
        except APIException as e:
            print('api')
            service_logger.warning("<Response [{}] >".format(e))
            raise e
        except HTTPException as e:
            code = e.code
            msg = e.description
            error_code = 20000
            service_logger.warning("<Response [{}]>".format(e))
            raise APIException(msg, code, error_code)
        except Exception as e:
            # print('eeee')
            service_logger.critical("<Response [500 Internal Server Error]>")
            error_logger.error(_request_log(request))
            error_logger.error(e, exc_info=True)
            raise UnknownException()

    return wrapper


def authentication(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not hasattr(g, "token"):
            raise AuthFailed("Token not found")

        if g.token.value != 'aabbcc':
            raise AuthFailed("您的身份认证已经失效， 请重新登录")
        return view(*args, **kwargs)

    return wrapper


def _request_log(request):
    data = 'Request({}): [{}] {} Args: {} Body: {}'.format(
        _get_requester(request),
        request.method,
        request.full_path,
        request.args.to_dict(),
        request.json
    )
    return data


def _get_requester(request):
    requester = request.remote_addr
    try:
        if hasattr(g, 'token'):
            requester = g.token.name
    finally:
        return requester
