# -*- coding: utf-8 -*-
from flask_micron import plugin
from tests import MicronTestCase


class DummyPlugin(plugin.Plugin):

    def start_request(self, ctx):
        if ctx.config.get('dommy', None) == 'yo':
            ctx.config['dommy'] = 'mister'

    def process_output(self, ctx):
        ctx.output = 'I made it, %s' % ctx.config['dommy']


class Tests(MicronTestCase):

    def test_HookMethodsInPluginsAreCalledViaMicron(self):
        self.micron.plugin(DummyPlugin())
        self.decorate(lambda: 'hi', rule='/hi', dommy='yo', csrf=False)
        response = self.request('/hi')
        self.assertEqual('I made it, mister', response.output)
