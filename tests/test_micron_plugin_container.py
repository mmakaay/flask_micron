# -*- coding: utf-8 -*-
import unittest
from flask_micron import plugin
from flask_micron.method import MicronMethodConfig


class Tests(unittest.TestCase):

    def test_CanCheckForContainmentBasedOnType(self):
        container = plugin.Container()
        dummy = Dummy()
        dommy = Dummy()
        ducky = Ducky()

        self.assertFalse(Ducky in container)
        self.assertFalse(ducky in container)
        self.assertFalse(dommy in container)
        self.assertFalse("Thing" in container)
        self.assertFalse(Dummy in container)
        self.assertFalse(dummy in container)
        self.assertFalse(object in container)

        container._plugins = [dummy]
        self.assertFalse(Ducky in container)
        self.assertFalse(ducky in container)
        self.assertFalse(dommy in container)
        self.assertFalse("Thing" in container)
        self.assertTrue(Dummy in container)
        self.assertTrue(dummy in container)
        self.assertTrue(object in container)

    def test_CanRegisterPluginWithContainer(self):
        container = plugin.Container()
        container.add(Dummy())
        self.assertTrue(Dummy in container)

    def test_HookMethodsInPluginsCanBeRun(self):
        container = plugin.Container()
        container.add(Dummy())
        config = MicronMethodConfig(dommy='yo')
        ctx = plugin.Context()
        ctx.config = config
        container.call_all(ctx, 'process_output')
        self.assertEqual('I made it, yo', ctx.output)

    def test_PluginsCanBeDuckTyped(self):
        container = plugin.Container()
        container.add(Ducky())
        config = MicronMethodConfig()
        ctx = plugin.Context()
        ctx.config = config
        container.call_all(ctx, 'normalize_input')
        container.call_all(ctx, 'process_output')
        self.assertEqual('Quack!', ctx.output)

    def test_CallAllVisitsAllPlugins(self):
        container = plugin.Container()
        container.add(
            CallAllTestPlugin('A'),
            CallAllTestPlugin('B'),
            CallAllTestPlugin('C'))
        ctx = plugin.Context()
        ctx.input = 'START';
        container.call_all(ctx, 'normalize_input');
        self.assertEqual('START|A|B|C', ctx.input);

    def test_CallOneFollowsChainOfCommandPattern(self):
        container = plugin.Container()
        container.add(
            CallOneTestPlugin('A', True),
            CallOneTestPlugin('B', True),
            CallOneTestPlugin('C', False))
        ctx = plugin.Context()
        container.call_one(ctx, 'read_input', 'input');
        self.assertEqual('B', ctx.input);

    def test_callOneAcceptsSettingMonitorFieldToNoneValue(self):
        container = plugin.Container()
        container.add(
            CallOneTestPlugin('A', True),
            CallOneTestPlugin('B', True),
            CallOneTestPlugin(None, True))
        ctx = plugin.Context()
        self.assertFalse(ctx.has('input'))
        container.call_one(ctx, 'read_input', 'input');
        self.assertTrue(ctx.has('input'))
        self.assertEqual(None, ctx.input);


class Dummy(plugin.Plugin):

    def process_output(self, ctx):
        ctx.output = 'I made it, %s' % ctx.config.dommy


class Ducky(object):
    """This is a duck typed plugin, meaning that it does not derive
    from the Plugin class. Additionally, it does not implement all
    the expected attributes.

    Strictly speaking we're not duck typing, but kind of the reverse
    here: the container doesn't assume that an attribute that we expect
    exists, but instead ignores missing ones.
    """
    def process_output(self, ctx):
        ctx.output = 'Quack!'


class CallAllTestPlugin(plugin.Plugin):

    def __init__(self, data):
        self.data = data

    def normalize_input(self, ctx):
        ctx.input = ctx.input + "|" + self.data


class CallOneTestPlugin(plugin.Plugin):

    def __init__(self, data, handle=True):
        self.handle = handle
        self.data = data

    def read_input(self, ctx):
        if self.handle:
            ctx.input = self.data
