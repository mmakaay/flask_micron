from flask import session
from flask_micron.plugins import csrf
from tests import MicronTestCase

class Tests(MicronTestCase):

    def test_GivenNoStoredTokens_StoreStoresToken(self):
        csrf._store_token('1', session)
        self.assertEqual(['1'], csrf._get_tokens(session))

    def test_GivenStoredTokens_StoreStoresAdditionalToken(self):
        csrf._store_token('1', session)
        csrf._store_token('2', session)
        self.assertEqual(['1', '2'], csrf._get_tokens(session))

    def test_GivenMaxAllowedStoredTokens_StoreStoresNewAndPopsOldToken(self):
        csrf.MAX_NUMBER_OF_CSRF_TOKENS_TO_STORE = 2
        csrf._store_token('1', session)
        csrf._store_token('2', session)
        csrf._store_token('3', session)
        self.assertEqual(['2', '3'], csrf._get_tokens(session))
