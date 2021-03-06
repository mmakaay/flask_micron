# -*- coding: utf-8 -*-
from flask_micron import plugins
from tests import MicronTestCase

# TODO Not for this test class, but reminder: fix conflict when creating two lambda methods (endpoints conflict).

class Tests(MicronTestCase):

    def setUp(self):
        super(Tests, self).setUp()
        self.micron.plugins.add(plugins.csrf.Plugin())

        @self.micron.method(csrf=True)
        def with_check():
            return 1

        @self.micron.method(csrf=False)
        def without_check():
            return 2

    def test_GivenDisabledCsrfCheck_CheckSucceeds(self):
        response = self.request('/without_check')
        self.assertEqual(2, response.output)

    def test_GivenMissingCsrfTokenInRequestAndEmptySession_CheckFails(self):
        response = self.request('/with_check')
        self.assertEqual('CsrfTokenRequired', response.output['code'])

    def test_GivenMissingCsrfTokenInRequest_CheckFails(self):
        self._add_csrf_tokens_to_session(['a', 'couple', 'of' 'tokens'])
        response = self.request('/with_check')
        self.assertEqual('CsrfTokenRequired', response.output['code'])

    def test_GivenInvalidCsrfTokenInRequestAndEmptySession_CheckFails(self):
        response = self.request('/with_check',
            headers={plugins.csrf.CSRF_TOKEN_HEADER: 'this-aint-a-valid-token'})
        self.assertEqual('CsrfTokenInvalid', response.output['code'])

    def test_GivenInvalidCsrfTokenInRequest_CheckFails(self):
        self._add_csrf_tokens_to_session(['a', 'couple', 'of' 'tokens'])
        response = self.request('/with_check',
            headers={plugins.csrf.CSRF_TOKEN_HEADER: 'this-aint-a-valid-token'})
        self.assertEqual('CsrfTokenInvalid', response.output['code'])

    def test_GivenValidCsrfTokenInRequest_CheckSucceeds(self):
        self._add_csrf_tokens_to_session(['these', 'are', 'valid'])
        response = self.request('/with_check',
            headers={plugins.csrf.CSRF_TOKEN_HEADER: 'valid'})
        self.assertEqual(1, response.output)

    def _add_csrf_tokens_to_session(self, tokens):
        with self.editable_session() as session:
            session[plugins.csrf.SESSION_KEY] = tokens
