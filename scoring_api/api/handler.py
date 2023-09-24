import json
import uuid
from http.server import BaseHTTPRequestHandler
import logging
import hashlib
import datetime

from scoring_api.api.constants import (
    ADMIN_SALT, SALT, OK, BAD_REQUEST,
    INTERNAL_ERROR, NOT_FOUND, ERRORS
)

logger = logging.getLogger(__name__)


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(
            datetime.datetime.now().strftime('%Y%m%d%H') + ADMIN_SALT
        ).hexdigest()
    else:
        digest = hashlib.sha512(
            request.account + request.login + SALT
        ).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    response, code = None, None
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
                        {'body': request, 'headers': self.headers},
                        context,
                        self.store
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
        self.wfile.write(json.dumps(r))
        return
