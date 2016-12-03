# -*- coding: utf-8 -*-
import unittest
from flask import Flask
from flask import json
from flask_micron import Micron
from flask_micron.errors import ImplementationError
from flask_micron.plugins import json_input
from flask_micron.plugins import normalize_input
from flask_micron.plugins import call_function
from flask_micron.plugins import json_output


class Tests(unittest.TestCase):

    def test_AutoloadedPlugins(self):
        autoloaded_plugins = Micron().plugins
        self.assertEqual(4, len(autoloaded_plugins))
        self.assertTrue(json_input.Plugin in autoloaded_plugins)
        self.assertTrue(normalize_input.Plugin in autoloaded_plugins)
        self.assertTrue(call_function.Plugin in autoloaded_plugins)
        self.assertTrue(json_output.Plugin in autoloaded_plugins)

    def test_DecoratorCanOnlyBeUsedWhenFlaskAppIsLinkedToMicron(self):
        micron = Micron()
        with self.assertRaises(ImplementationError):
            @micron.method()
            def f():
                pass

    def test_SettingsArePassedToDecoratedMethods(self):
        app = Flask('TestApp')
        micron = Micron(app, option1='y', option2='z')
        micron.plugin(ConfigSpy())

        @micron.method()
        def f():
            pass

        response = micron.app.test_client().post('/f')
        config = json.loads(response.data)

        self.assertEqual({
            'option1': 'y',
            'option2': 'z'
        }, config)

    def test_SettingsCanBeOverriddenInDecorator(self):
        app = Flask('TestApp')
        micron = Micron(app, option1='x', option2='y', option3='z')
        micron.plugin(ConfigSpy())

        @micron.method(option1='b', option2=None)
        def f():
            pass

        response = micron.app.test_client().post('/f')
        config = json.loads(response.data)

        self.assertEqual({
            'option1': 'b',
            'option2': None,
            'option3': 'z'
        }, config)


class ConfigSpy(object):
    def process_output(self, ctx):
        ctx.output = ctx.config
