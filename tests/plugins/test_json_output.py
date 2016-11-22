# pylint: disable=no-member
# No idea what triggers the error in _call_plugin():
# Instance of 'str' has no 'data' member (no-member)

from datetime import datetime
from datetime import timedelta
import unittest
from flask import json
from flask_micron.plugins import json_output
from flask_micron.errors import ImplementationError
from flask_micron.micron_plugin_context import MicronPluginContext


class JsonOutputTests(unittest.TestCase):

    def test_GivenNone_JsonNullIsReturned(self):
        response = self._call_plugin(None, None)
        self.assertEqual(b'null', response)

    def test_GivenString_JsonStringIsReturned(self):
        response = self._call_plugin("hey", None)
        self.assertEqual(b'"hey"', response)

    def test_GivenComplex_JsonComplexIsReturned(self):
        arg = {
            "key1": "value1",
            "key2": "value2"
        }
        response = self._call_plugin(arg, None)
        output = json.loads(response.decode('utf-8'))
        self.assertEqual(arg, output)

    def _call_plugin(self, output, error):
        ctx = MicronPluginContext()
        ctx.output = output
        ctx.error = error
        json_output.Plugin().create_response(ctx)
        return ctx.response.data


class SerializerHookTests(unittest.TestCase):

    def test_str(self):
        self.assertEqual(
            'this is it',
            json_output._serializer_hook('this is it'))

    def test_bytes(self):
        self.assertEqual(
            'this is it',
            json_output._serializer_hook(b'this is it'))

    def test_datetime(self):
        d = datetime(2000, 1, 2, 10, 11, 12)
        self.assertEqual(
            '2000-01-02T10:11:12',
            json_output._serializer_hook(d))

    def test_timedelta(self):
        d = timedelta(1, 2, 3)
        self.assertEqual(
            '1 day, 0:00:02.000003',
            json_output._serializer_hook(d))

    def test_unsupported_type(self):
        with self.assertRaises(ImplementationError):
            json_output._serializer_hook(object())
