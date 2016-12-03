# -*- coding: utf-8 -*-
from flask_micron.plugins import csrf
import unittest


class Tests(unittest.TestCase):

    def setUp(self):
        self.header_name = csrf.CSRF_TOKEN_HEADER

    def test_GivenUpperCaseHeader_HeaderIsReturned(self):
        upper = str.upper(csrf.CSRF_TOKEN_HEADER)
        extracted = csrf._extract_token_from_headers({upper: 'GOT IT'})
        self.assertEqual('GOT IT', extracted)

    def test_GivenLowerCaseHeader_HeaderIsReturned(self):
        lower = str.lower(self.header_name)
        extracted = csrf._extract_token_from_headers({lower: 'got it'})
        self.assertEqual('got it', extracted)

    def test_GivenNoHeader_NoneIsReturned(self):
        extracted = csrf._extract_token_from_headers({'X-Poke': 'Mon'})
        self.assertIsNone(extracted)
