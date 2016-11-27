# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name

import unittest
import flask_micron
from flask_micron.method import MicronMethodConfig


class Tests(unittest.TestCase):

    def test_PluginMethods(self):
        """Check if we only get back those methods that we consider
        plugin hooks from the base plugin class.
        """
        d = flask_micron.Plugin.__dict__
        self.assertEqual({
            'start_request': d['start_request'],
            'check_access': d['check_access'],
            'after_check_access': d['after_check_access'],
            'read_input': d['read_input'],
            'normalize_input': d['normalize_input'],
            'validate_input': d['validate_input'],
            'call_function': d['call_function'],
            'process_output': d['process_output'],
            'create_response': d['create_response'],
            'process_error': d['process_error'],
            'process_response': d['process_response'],
            'end_request': d['end_request']
        }, flask_micron.plugin.PLUGIN_METHODS)

    def test_CompileEmptyPlugin(self):

        class EmptyPlugin(flask_micron.Plugin):
            pass

        hooks = flask_micron.plugin.Compiler().compile(EmptyPlugin())

        # Check for extraction of the correct hook functions.
        self.assertEqual({}, hooks)

    def test_CompileEmptyDuckTypedPlugin(self):

        class EmptyDuckTypedPlugin(object):
            pass

        hooks = flask_micron.plugin.Compiler().compile(EmptyDuckTypedPlugin())

        # Check for extraction of the correct hook functions.
        self.assertEqual({}, hooks)

    def test_CompileDerivedPlugin(self):

        class DerivedPlugin(flask_micron.Plugin):
            def normalize_input(self, ctx):
                ctx.input = "DerivedPlugin input %s" % ctx.config.option1
            def process_output(self, ctx):
                ctx.output = "%s %s" % (ctx.config.option1, ctx.config.option2)

        hooks = flask_micron.plugin.Compiler().compile(DerivedPlugin())

        # Check for extraction of the correct hook functions.
        self.assertEqual(
            {'normalize_input', 'process_output'},
            set(hooks.keys()))

        # Check if the compiled hook functions can be called.
        config = MicronMethodConfig(option1='value1', option2='value2')
        ctx = flask_micron.plugin.Context()
        ctx.config = config
        ctx.input = 'orig input'
        hooks['normalize_input'](ctx)
        self.assertEqual('DerivedPlugin input value1', ctx.input)
        self.assertEqual(None, ctx.output)
        hooks['process_output'](ctx)
        self.assertEqual('DerivedPlugin input value1', ctx.input)
        self.assertEqual('value1 value2', ctx.output)

    def test_CompileDuckTypedPlugin(self):
        class DuckTypedPlugin(object):
            def normalize_input(self, ctx):
                duck = ctx.config.duck
                ctx.input = "DuckTypedPlugin input %s" % duck

        hooks = flask_micron.plugin.Compiler().compile(DuckTypedPlugin())

        # Check for extraction of the correct hook functions.
        self.assertEqual({'normalize_input'}, set(hooks.keys()))

        # Check if the compiled hook functions can be called.
        config = MicronMethodConfig(duck='Dagobert')
        ctx = flask_micron.plugin.Context()
        ctx.config = config
        hooks['normalize_input'](ctx)
        self.assertEqual('DuckTypedPlugin input Dagobert', ctx.input)

    def test_CompileConstructedPlugin(self):
        def process_output(ctx):
            ctx.output = ctx.config.drill
        class ConstructedPlugin:
            def __init__(self):
                self.process_output = process_output

        hooks = flask_micron.plugin.Compiler().compile(ConstructedPlugin())

        # Check for extraction of the correct hook functions.
        self.assertEqual({'process_output'}, set(hooks.keys()))

        # Check if the compiled hook functions can be called.
        config = MicronMethodConfig(drill=True)
        ctx = flask_micron.plugin.Context()
        ctx.config = config
        hooks['process_output'](ctx)
        self.assertEqual(True, ctx.output)

    def test_CompileDictPlugin(self):
        def process_output(ctx):
            simple = ctx.config.simple
            ctx.output = simple * simple
        dict_plugin = {
            'process_output': process_output
        }

        hooks = flask_micron.plugin.Compiler().compile(dict_plugin)

        # Check for extraction of the correct hook functions.
        self.assertEqual({'process_output'}, set(hooks.keys()))

        # Check if the compiled hook functions can be called.
        config = MicronMethodConfig(simple=11)
        ctx = flask_micron.plugin.Context()
        ctx.config = config
        hooks['process_output'](ctx)
        self.assertEqual(121, ctx.output)

    def test_ModulePlugin(self):
        module = globals()
        hooks = flask_micron.plugin.Compiler().compile(module)

        # Check for extraction of the correct hook functions.
        self.assertEqual(
            {'normalize_input', 'process_output'},
            set(hooks.keys()))

        # Check if the compiled hook functions can be called.
        ctx = flask_micron.plugin.Context()
        hooks['normalize_input'](ctx)
        hooks['process_output'](ctx)
        self.assertEqual(256, ctx.output)


# These functions after used to make this module work as a Micron plugin.
# The test_ModulePlugin() makes use of it.

def normalize_input(ctx):
    ctx.input = 16

def process_output(ctx):
    ctx.output = ctx.input * ctx.input
