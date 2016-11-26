# -*- coding: utf-8 -*-
from flask_micron import plugin
from tests import MicronTestCase


class Tests(MicronTestCase):

    def setUp(self):
        super(Tests, self).setUp()
        self.ctx = plugin.Context()

    def test_NewContextHasNoConfig(self):
        self.assertIsNone(self.ctx.config)
        self.assertFalse(self.ctx.has('config'))

    def test_ContextCanGetConfig(self):
        self.ctx.config = 'yo'
        self.assertEqual('yo', self.ctx.config)
        self.assertTrue(self.ctx.has('config'))

    def test_NewContextHasNoFunction(self):
        self.assertIsNone(self.ctx.function)
        self.assertFalse(self.ctx.has('function'))

    def test_ContextCanGetFunction(self):
        self.ctx.function = 'hey'
        self.assertEqual('hey', self.ctx.function)
        self.assertTrue(self.ctx.has('function'))

    def test_NewContextHasNoInput(self):
        self.assertIsNone(self.ctx.input)
        self.assertFalse(self.ctx.has('input'))

    def test_ContextCanGetInput(self):
        self.ctx.input = {'arg': 'value'}
        self.assertEqual({'arg': 'value'}, self.ctx.input)
        self.assertTrue(self.ctx.has('input'))

    def test_ContextCanGetInputEqualToNone(self):
        self.ctx.input = None
        self.assertIsNone(self.ctx.input)
        self.assertTrue(self.ctx.has('input'))

    def test_NewContextHasNoOutput(self):
        self.assertIsNone(self.ctx.output)
        self.assertFalse(self.ctx.has('output'))

    def test_ContextCanGetOutput(self):
        self.ctx.output = 'hi'
        self.assertEqual('hi', self.ctx.output)
        self.assertTrue(self.ctx.has('output'))

    def test_NewContextHasNoResponse(self):
        self.assertIsNone(self.ctx.response)
        self.assertFalse(self.ctx.has('response'))

    def test_ContextCanGetResponse(self):
        self.ctx.response = 'bye'
        self.assertEqual('bye', self.ctx.response)
        self.assertTrue(self.ctx.has('response'))

    def test_NewContextHasNoError(self):
        self.assertIsNone(self.ctx.error)
        self.assertFalse(self.ctx.has('error'))

    def test_ContextCanGetError(self):
        self.ctx.error = Exception("Broken?")
        self.assertEqual('Broken?', str(self.ctx.error))
        self.assertTrue(self.ctx.has('error'))
