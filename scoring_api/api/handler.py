import datetime
import hashlib
import json
import logging
import uuid
from http.server import BaseHTTPRequestHandler

from scoring_api.api.api import (
    ClientsInterestsRequest,
    MethodRequest,
    OnlineScoreRequest,
)
from scoring_api.api.constants import (
    ADMIN_SALT,
    BAD_REQUEST,
    ERRORS,
    FORBIDDEN,
    INTERNAL_ERROR,
    INVALID_REQUEST,
    NOT_FOUND,
    OK,
    SALT,
)
from scoring_api.api.scoring import get_interests, get_score

logger = logging.getLogger(__name__)


def check_auth(request: MethodRequest):
    if request.is_admin:
        digest = hashlib.sha512(
            (datetime.datetime.now().strftime('%Y%m%d%H') + ADMIN_SALT).encode()
        ).hexdigest()
    else:
        digest = hashlib.sha512(
            (request.account + request.login + SALT).encode()
        ).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request: dict, ctx: dict, store):
    """Dispatches request processing to specific handlers"""
    response, code = None, OK
    try:
        method_request = MethodRequest(**request['body'])
    except ValueError as e:
        response, code = str(e), INVALID_REQUEST
    else:
        if check_auth(method_request):
            if method_request.method == 'online_score':
                response, code = online_score_handler(
                    method_request, ctx, store
                )
            elif method_request.method == 'clients_interests':
                response, code = clients_interests_handler(
                    method_request, ctx, store
                )
            else:
                code = NOT_FOUND
        else:
            code = FORBIDDEN
    return response, code


def online_score_handler(method_request: MethodRequest, ctx: dict, store):
    """Processes client scoring request"""
    response, code = None, OK
    try:
        request = OnlineScoreRequest(**method_request.arguments)
    except ValueError as e:
        response, code = str(e), INVALID_REQUEST
    else:
        ctx.update(
            has=list(method_request.arguments.keys())
        )
        if method_request.is_admin:
            response = dict(
                score=42
            )
        else:
            response = dict(
                score=get_score(
                    store=store,
                    phone=request.phone,
                    email=request.email,
                    birthday=request.birthday,
                    gender=request.gender,
                    first_name=request.first_name,
                    last_name=request.last_name
                )
            )
    return response, code


def clients_interests_handler(method_request: MethodRequest, ctx: dict, store):
    """Processes client interests request"""
    response, code = None, OK
    try:
        request = ClientsInterestsRequest(**method_request.arguments)
    except ValueError as e:
        response, code = str(e), INVALID_REQUEST
    else:
        ctx.update(
            nclients=len(request.client_ids)
        )
        response = {
            client_id: get_interests(store, client_id)
            for client_id in request.client_ids
        }
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        'method': method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {'request_id': self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip('/')
            logger.info(
                '%s: %s %s',
                self.path, data_string, context['request_id']
            )
            if path in self.router:
                try:
                    response, code = self.router[path](
                        request={'body': request, 'headers': self.headers},
                        ctx=context,
                        store=self.store
                    )
                except Exception as e:
                    logger.exception('Unexpected error: %s', e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        if code not in ERRORS:
            r = dict(
                response=response,
                code=code
            )
        else:
            r = dict(
                error=response or ERRORS.get(code, 'Unknown Error'),
                code=code
            )
        context.update(r)
        logger.info(context)
        self.wfile.write(json.dumps(r).encode())
        return
