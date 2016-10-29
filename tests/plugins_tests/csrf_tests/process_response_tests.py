from flask_micron.plugins import csrf
from flask import session
from tests import MicronTestCase
import json


class Tests(MicronTestCase):

    def setUp(self):
        super().setUp()

        @self.micron.method(csrf=False)
        def dummy():
            pass

    def test_AfterRequestHook_StoresNewTokenInSession(self):
        self.assertEqual(0, len(csrf._get_tokens(session)))

        with self.client:
            self.request('/dummy')
            tokens_in_store = csrf._get_tokens(session)
        self.assertEqual(1, len(tokens_in_store))
        new_token = tokens_in_store[0]
        self.assertTrue(isinstance(new_token, str))
        self.assertEqual(36, len(new_token))

    def test_AfterRequestHook_AddsNewTokenToHeaders(self):
        with self.client:
            response = self.request('/dummy')
            tokens_in_store = csrf._get_tokens(session)
        token_in_store = tokens_in_store[-1]
        token_in_header = response.headers['X-Micron-CSRF-Token']
        self.assertEqual(token_in_store, token_in_header)
