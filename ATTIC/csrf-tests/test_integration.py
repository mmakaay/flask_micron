# -*- coding: utf-8 -*-
from flask_micron.plugins import csrf
from tests import MicronTestCase


class Tests(MicronTestCase):

    def setUp(self):
        super(Tests, self).setUp()

        @self.micron.method(csrf=True)
        def greet(who='World'):
            return 'Hello, %s' % who

    def test_CallMethod_WithFailingCsrfCheck(self):
        response = self.request('/greet', "me")
        self.assertEqual(500, response.status_code)
        self.assertEqual('CsrfTokenRequired', response.output['code'])

    def test_CallMethod_WithSucceedingCsrfCheck(self):
        # Call the /ping method.
        response = self.request('/ping')

        # This will return 'pong' and a new CSRF token.
        self.assertEqual('pong', response.output)
        self.assertIsNotNone(response.headers[csrf.CSRF_TOKEN_HEADER])
        token = response.headers[csrf.CSRF_TOKEN_HEADER]

        # Call the /greet method with some input and the received CSRF token. 
        headers = {csrf.CSRF_TOKEN_HEADER: token}
        response = self.request('/greet', "me", headers=headers)

        # This will return a greeting.
        self.assertEqual('Hello, me', response.output)
