# -*- coding: utf-8 -*-
from flask_micron.plugins import normalize_input
from tests import MicronTestCase


class Tests(MicronTestCase):

    def test_GivenNone_NoneIsReturned(self):
        self._assertNormalized(None, None)

    def test_GivenEmptyString_NoneIsReturned(self):
        self._assertNormalized(None, '')

    def test_GivenWhitespaceString_NoneIsReturned(self):
        self._assertNormalized(None, " \t \n ")

    def test_GivenWhitespaceAroundString_TrimmedStringIsReturned(self):
        self._assertNormalized('The Value', " \t The Value \n ")

    def test_GivenDict_NormalizedDictIsReturned(self):
        self._assertNormalized({
            'key1': None,
            'key2': None,
            'key3': None,
            'key4': 'value4'
        }, {
            'key1': None,
            'key2': '',
            'key3': ' ',
            'key4': ' value4 '
        })


    def test_GivenList_NormalizedListIsReturned(self):
        self._assertNormalized([
            'value1',
            'value2',
            None
        ], [
            ' value1\n   \t ',
            'value2',
            '               ',
        ])


    def test_GivenNestedData_NormalizedNestedDataIsReturned(self):
        self._assertNormalized({
            'key1': 'value1',
            'key2': {
                'key3': 'value3',
                'key4': [
                    'value4.1',
                    'value4.2',
                    None
                ]
            }
        }, {
            'key1': ' value1 ',
            'key2': {
                'key3': ' value3 ',
                'key4': [
                    ' value4.1 ',
                    'value4.2',
                    ' '
                ]
            }
        })

    def _assertNormalized(self, expected, arg):
        self.assertEqual(
            expected,
            normalize_input._normalize(arg, True, True))

    def test_Integration(self):
        @self.micron.method()
        def echo(arg):
            return arg

        response = self.request("/echo", {"my": " yo1 ", "mi": " hey "})
        self.assertEqual({"my": "yo1", "mi": "hey"}, response.output)

    def test_Configuration_Normalize(self):
        @self.micron.method(
            normalize=False)
        def echo(arg):
            return arg

        response = self.request('/echo', {"my": " yo1 ", "mi": ""})
        self.assertEqual({"my": " yo1 ", "mi": ""}, response.output)

    def test_Configuration_StripStrings(self):
        @self.micron.method(
            strip_strings=False,
            make_empty_strings_none=True)
        def echo(arg):
            return arg

        response = self.request('/echo', {"my": " yo1 "})
        self.assertEqual({"my": " yo1 "}, response.output)

    def test_Configuration_MakeEmptyNone(self):
        @self.micron.method(
            strip_string=True,
            make_empty_strings_none=False)
        def echo(arg):
            return arg

        response = self.request('/echo', {"my": " \t\r\n "})
        self.assertEqual({"my": ""}, response.output)
