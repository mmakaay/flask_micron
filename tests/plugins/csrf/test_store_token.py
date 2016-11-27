# -*- coding: utf-8 -*-
from flask import session
from flask_micron.plugins import csrf
from tests import MicronTestCase


class Tests(MicronTestCase):

    def test_GivenNoStoredTokens_StoreStoresToken(self):
        csrf._store_token('1')
        self.assertEqual(['1'], csrf._get_tokens())

    def test_GivenStoredTokens_StoreStoresAdditionalToken(self):
        csrf._store_token('1')
        csrf._store_token('2')
        self.assertEqual(['1', '2'], csrf._get_tokens())

    def test_GivenMaxAllowedStoredTokens_StoreStoresNewAndPopsOldToken(self):
        csrf.MAX_NUMBER_OF_CSRF_TOKENS_TO_STORE = 2
        csrf._store_token('1')
        csrf._store_token('2')
        csrf._store_token('3')
        self.assertEqual(['2', '3'], csrf._get_tokens())
