from flask import json
from flask_micron.plugins import csrf
from tests import MicronTestCase

# TODO Not for this test class, but reminder: fix conflict when creating two lambda methods (endpoints conflict).

class Tests(MicronTestCase):

    def setUp(self):
        super().setUp()

        @self.micron.method(csrf=True)
        def with_check():
            return 1

        @self.micron.method(csrf=False)
        def without_check():
            return 2

    def test_GivenDisabledCsrfCheck_CheckSucceeds(self):
        response = self.request('/without_check')
        self.assertEquals(2, response.output)

    def test_GivenMissingCsrfTokenInRequestAndEmptySession_CheckFails(self):
        response = self.request('/with_check')
        self.assertEquals('CsrfTokenRequired', response.output['code'])

    def test_GivenMissingCsrfTokenInRequest_CheckFails(self):
        self._add_csrf_tokens_to_session(['a', 'couple', 'of' 'tokens'])
        response = self.request('/with_check')
        self.assertEquals('CsrfTokenRequired', response.output['code'])

    def test_GivenInvalidCsrfTokenInRequestAndEmptySession_CheckFails(self):
        response = self.request('/with_check',
            headers={csrf.CSRF_TOKEN_HEADER: 'this-aint-a-valid-token'})
        self.assertEquals('CsrfTokenInvalid', response.output['code'])

    def test_GivenInvalidCsrfTokenInRequest_CheckFails(self):
        self._add_csrf_tokens_to_session(['a', 'couple', 'of' 'tokens'])
        response = self.request('/with_check',
            headers={csrf.CSRF_TOKEN_HEADER: 'this-aint-a-valid-token'})
        self.assertEquals('CsrfTokenInvalid', response.output['code'])

    def test_GivenValidCsrfTokenInRequest_CheckSucceeds(self):
        self._add_csrf_tokens_to_session(['these', 'are', 'valid'])
        response = self.request('/with_check',
            headers={csrf.CSRF_TOKEN_HEADER: 'valid'})
        self.assertEquals(1, response.output)

    def _add_csrf_tokens_to_session(self, tokens):
        with self.editable_session() as session:
            session[csrf.SESSION_KEY] = json.dumps(tokens)
