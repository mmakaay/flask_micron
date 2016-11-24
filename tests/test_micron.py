# -*- coding: utf-8 -*-
import unittest
from flask import Flask
from flask import json
from flask_micron import Micron
from flask_micron.errors import ImplementationError
from flask_micron.plugins import csrf
from flask_micron.plugins import normalize_input


class Tests(unittest.TestCase):

    def test_MicronLoadsCrsfPluginAutomatically(self):
        self.assertTrue(csrf.Plugin in Micron().plugins)

    def test_MicronLoadNormalizeInputluginAutomatically(self):
        self.assertTrue(normalize_input.Plugin in Micron().plugins)

    def test_DecoratorCanOnlyBeUsedWhenFlaskAppIsLinkedToMicron(self):
        micron = Micron()
        with self.assertRaises(ImplementationError):
            @micron.method()
            def f():
                pass

    def test_SettingsArePassedToDecoratedMethods(self):
        app = Flask('TestApp')
        app.secret_key = "Let's see this config trick"
        micron = Micron(app, csrf=False, option1='y', option2='z')
        micron.plugin(ConfigSpy())

        @micron.method()
        def f():
            pass

        response = micron.app.test_client().post('/f')
        config = json.loads(response.data)

        self.assertEqual({
            'csrf': False,
            'option1': 'y',
            'option2': 'z'
        }, config)

    def test_SettingsCanBeOverriddenInDecorator(self):
        app = Flask('TestApp')
        app.secret_key = "Let's see this config trick"
        micron = Micron(app, csrf=False, option1='y', option2='z')
        micron.plugin(ConfigSpy())

        @micron.method(option1='b', option2=None)
        def f():
            pass

        response = micron.app.test_client().post('/f')
        config = json.loads(response.data)

        self.assertEqual({
            'csrf': False,
            'option1': 'b',
            'option2': None
        }, config)

    def test_DefaultPlugins_ReturnOnlyPostForRequestMethods(self):
        micron = Micron(Flask('TestApp'))
        methods = micron.get_request_methods()
        self.assertEqual(['POST'], methods)

    def test_WhenPluginReturnsNoneForRequestMethods_ExceptionIsRaised(self):
        micron = Micron(Flask('TestApp'))
        micron.plugin(GetRequestMethodsPlugin(None))
        with self.assertRaises(ImplementationError):
            micron.get_request_methods()

class GetRequestMethodsPlugin(object):
    def __init__(self, methods):
        self.methods = methods

    def request_methods(self, _):
        return self.methods 


class ConfigSpy(object):
    def process_output(self, ctx):
        ctx.output = ctx.config
