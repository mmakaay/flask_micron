# -*- coding: utf-8 -*-
import unittest
from flask_micron import compat


class Tests(unittest.TestCase):

    def test_IsString(self):
        self.assertTrue(compat.is_string(""))
        self.assertTrue(compat.is_string(u""))
        self.assertTrue(compat.is_string(b""))
        self.assertFalse(compat.is_string(None))
        self.assertFalse(compat.is_string(object()))
