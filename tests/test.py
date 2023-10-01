import datetime
import hashlib

from scoring_api.api import constants, handler


class TestSuite:
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.settings = {}

    def get_response(self, request):
        return handler.method_handler(
            request=dict(
                body=request,
                headers=self.headers
            ),
            ctx=self.context,
            store=self.settings
        )

    def set_valid_auth(self, request):
        if request.get('login') == constants.ADMIN_LOGIN:
            request['token'] = hashlib.sha512((
                datetime.datetime.now().strftime('%Y%m%d%H')
                + constants.ADMIN_SALT
            ).encode('utf-8')).hexdigest()
        else:
            msg = (
                request.get('account', '')
                + request.get('login', '')
                + constants.SALT
            )
            request['token'] = hashlib.sha512(msg.encode('utf-8')).hexdigest()

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(constants.INVALID_REQUEST, code)

    def test_bad_auth(self, request):
        _, code = self.get_response(request)
        self.assertEqual(constants.FORBIDDEN, code)

    def test_invalid_method_request(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(constants.INVALID_REQUEST, code)
        self.assertTrue(len(response))

    def test_invalid_score_request(self, arguments):
        request = {
            'account': 'horns&hoofs',
            'login': 'h&f',
            'method': 'online_score',
            'arguments': arguments
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(constants.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))

    def test_ok_score_request(self, arguments):
        request = {
            'account': 'horns&hoofs',
            'login': 'h&f',
            'method': 'online_score',
            'arguments': arguments
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(constants.OK, code, arguments)
        score = response.get('score')
        self.assertTrue(
            isinstance(score, (int, float)) and score >= 0, arguments
        )
        self.assertEqual(sorted(self.context['has']), sorted(arguments.keys()))

    def test_ok_score_admin_request(self):
        arguments = {'phone': '79175002040', 'email': 'stupnikov@otus.ru'}
        request = {
            'account': 'horns&hoofs',
            'login': 'admin',
            'method': 'online_score',
            'arguments': arguments
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(constants.OK, code)
        score = response.get('score')
        self.assertEqual(score, 42)

    def test_invalid_interests_request(self, arguments):
        request = {
            'account': 'horns&hoofs',
            'login': 'h&f',
            'method': 'clients_interests',
            'arguments': arguments
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(constants.INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))

    def test_ok_interests_request(self, arguments):
        request = {
            'account': 'horns&hoofs',
            'login': 'h&f',
            'method': 'clients_interests',
            'arguments': arguments
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(constants.OK, code, arguments)
        self.assertEqual(len(arguments['client_ids']), len(response))
        self.assertTrue(all(
            v
            and isinstance(v, list)
            and all(isinstance(i, (bytes, str)) for i in v)
            for v in response.values()
        ))
        self.assertEqual(
            self.context.get('nclients'),
            len(arguments['client_ids'])
        )
