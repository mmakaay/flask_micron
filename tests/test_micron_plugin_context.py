# -*- coding: utf-8 -*-
from flask_micron.micron_plugin_context import MicronPluginContext
from tests import MicronTestCase


class Tests(MicronTestCase):

    def setUp(self):
        super(Tests, self).setUp()
        self.ctx = MicronPluginContext()

    def test_NewContextHasNoInput(self):
        self.assertIsNone(self.ctx.input)

    def test_ExistingContextCanGetInput(self):
        self.ctx.input = {'arg': 'value'}
        self.assertEqual({'arg': 'value'}, self.ctx.input)

    def test_NewContextHasNoOutput(self):
        self.assertIsNone(self.ctx.output)

    def test_ExistingContextCanGetOutput(self):
        self.ctx.output = 'hi'
        self.assertEqual('hi', self.ctx.output)

    def test_NewContextHasNoResponse(self):
        self.assertIsNone(self.ctx.response)

    def test_ExistingContextCanGetResponse(self):
        self.ctx.response = 'bye'
        self.assertEqual('bye', self.ctx.response)

    def test_NewContextHasNoError(self):
        self.assertIsNone(self.ctx.error)

    def test_ExistingContextCanGetError(self):
        self.ctx.error = Exception("Broken?")
        self.assertEqual('Broken?', str(self.ctx.error))
