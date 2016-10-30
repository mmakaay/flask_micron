import unittest
from flask import Flask
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
        micron = Micron(Flask('TestApp'))
        micron.configure(csrf='x', option1='y', option2='z')

        @micron.method()
        def f():
            pass

        self.assertEqual('x', f.config.csrf)
        self.assertEqual('y', f.config.option1)
        self.assertEqual('z', f.config.option2)

    def test_SettingsCanBeOverriddenInDecorator(self):
        micron = Micron(Flask('TestApp'))
        micron.configure(csrf='x', option1='y', option2='z')

        @micron.method(csrf='a', option1='b', option2='c')
        def f():
            pass

        self.assertEqual('a', f.config.csrf)
        self.assertEqual('b', f.config.option1)
        self.assertEqual('c', f.config.option2)
