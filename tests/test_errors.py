# -*- coding: utf-8 -*-
import unittest
from flask_micron import MicronClientError
from flask_micron import MicronServerError
from flask_micron.errors import MicronError
from flask_micron.errors import ImplementationError


class TestClientError(MicronClientError):
    """TestClientError description."""


class TestServerError(MicronServerError):
    """TestServerError description."""


class Tests(unittest.TestCase):

    def test_MicronError(self):
        error = MicronError("client", "detail")
        self.assertEqual("client", error.caused_by)
        self.assertEqual("detail", error.details)
        self.assertEqual(
            "The root of all Micron evil.",
            error.description)

    def test_MicronErrorWithoutDetails(self):
        error = MicronError("server")
        self.assertIsNone(error.details)

    def test_MicronErrorWithInvalidCausedByValue_RaisesException(self):
        with self.assertRaises(ImplementationError):
            MicronError(caused_by="ignorance")

    def test_CustomMicronClientError(self):
        error = TestClientError(['my', 'error', 'details'])
        self.assertEqual("client", error.caused_by)
        self.assertEqual(['my', 'error', 'details'], error.details)
        self.assertEqual("TestClientError description.", error.description)

    def test_CustomMicronServerError(self):
        error = TestServerError({})
        self.assertEqual("server", error.caused_by)
        self.assertEqual({}, error.details)
        self.assertEqual("TestServerError description.", error.description)
