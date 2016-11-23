# -*- coding: utf-8 -*-
from tests import MicronTestCase


class Tests(MicronTestCase):

    def setUp(self):
        super(Tests, self).setUp()
        @self.micron.method(csrf=False, normalize=False)
        def echo(arg=None):
            return arg

    def test_GivenNone_NoneIsReturned(self):
        self._assertInputIsOutput(None)

    def test_GivenEmptyString_EmptyStringIsReturned(self):
        self._assertInputIsOutput('')

    def test_GivenString_StringIsReturned(self):
        self._assertInputIsOutput("My cool string")

    def test_GivenJsonDict_DictIsReturned(self):
        self._assertInputIsOutput({
            'key1': ' value1 ',
            'key2': '',
            'key3': None,
            'key4': [1, 2, 3]
        })

    def _assertInputIsOutput(self, arg):
        response = self.request('/echo', arg)
        self.assertEqual(arg, response.output)
