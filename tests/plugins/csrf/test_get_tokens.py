# -*- coding: utf-8 -*-
import unittest
from flask import session
from flask_micron.plugins import csrf
from tests import MicronTestCase


class Tests(MicronTestCase):

    def test_GivenNoStoredTokens_GetTokensReturnsEmptyList(self):
        session.pop(csrf.SESSION_KEY, None)
        self.assertEqual([], csrf._get_tokens())

    def test_GivenEmptyListOfStoredTokens_GetTokensReturnsEmptyList(self):
        self._add_csrf_tokens_to_session([])
        self.assertEqual([], csrf._get_tokens())

    def test_GivenSingleStoredToken_GetTokensReturnSingleToken(self):
        self._add_csrf_tokens_to_session(['one'])
        self.assertEqual(['one'], csrf._get_tokens())

    def test_GivenMultipleStoredToken_GetTokensReturnsMultpleToken(self):
        self._add_csrf_tokens_to_session(['one', 'two'])
        self.assertEqual(['one', 'two'], csrf._get_tokens())

    def _add_csrf_tokens_to_session(self, tokens):
        session[csrf.SESSION_KEY] = tokens
