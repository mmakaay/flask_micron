# -*- coding: utf-8 -*-
import unittest
from flask_micron.method import MicronMethodConfig
from flask_micron.errors import ImplementationError


class Tests(unittest.TestCase):

    def test_EmptyConfigCanBeCreated(self):
        MicronMethodConfig()

    def test_InvalidIdentifier_RaisesException(self):
        with self.assertRaises(ImplementationError):
            MicronMethodConfig(**{"I N V A L I D": "I D E N T I F I E R"})

    def test_GivenEmptyConfigValue_WhenRetrievingValue_ExceptionIsRaised(self):
        with self.assertRaises(KeyError):
            MicronMethodConfig().nosuchvalue

    def test_ValuesCanBeSetInTheConstructor(self):
        config = MicronMethodConfig(option1=2, option2=3)
        self.assertEqual(2, config.option1)
        self.assertEqual(3, config.option2)

    def test_ValuesCanBeSetUsingConfigure(self):
        config = MicronMethodConfig().configure(option1=2, option2=3)
        self.assertEqual(2, config.option1)
        self.assertEqual(3, config.option2)

    def test_ValuesCanBeSetUsingSetters(self):
        config = MicronMethodConfig()
        config.option1 = 2
        config.option2 = 3
        self.assertEqual(2, config.option1)
        self.assertEqual(3, config.option2)

    def test_WhenValueIsNotSet_ValueIsRetrievedFromParent(self):
        level1 = MicronMethodConfig(option1=2, option2=3)
        level2 = MicronMethodConfig(parent=level1, option1='a')
        level3 = MicronMethodConfig(parent=level2, option2='x')

        self.assertEqual(2, level1.option1)
        self.assertEqual(3, level1.option2)

        self.assertEqual('a', level2.option1)
        self.assertEqual(3, level2.option2)

        self.assertEqual('a', level3.option1)
        self.assertEqual('x', level3.option2)

    def test_DerivedConfigCanOverrideValueWithNoneValue(self):
        level1 = MicronMethodConfig().configure(option1=2, option2=3)
        level2 = MicronMethodConfig(parent=level1).configure(option1=None)

        self.assertEqual(2, level1.option1)
        self.assertEqual(3, level1.option2)

        self.assertEqual(None, level2.option1)
        self.assertEqual(3, level2.option2)

    def test_NewOptionsCanBeAdded(self):
        level1 = MicronMethodConfig()
        level2 = MicronMethodConfig(level1)
        level1.my = 'option'
        self.assertEqual('option', level1.my)
        self.assertEqual('option', level2.my)

    def test_OptionNamesProvidesListOfAllOptionsNamesInHierarchy(self):
        level1 = MicronMethodConfig(my='option')
        level2 = MicronMethodConfig(level1, another='option')
        level3 = MicronMethodConfig(level2, final='option')
        self.assertEqual(
            {'my'},
            level1.option_names)
        self.assertEqual(
            {'my', 'another'},
            level2.option_names)
        self.assertEqual(
            {'my', 'another', 'final'},
            level3.option_names)

    def test_FlattenedProvidesResolvedDictOfAllOptions(self):
        level1 = MicronMethodConfig(first='value1', one=1)
        level2 = MicronMethodConfig(level1, one='one', second='value2')
        level3 = MicronMethodConfig(level2, second='value two', third='value3')
        self.assertEqual({
            'first': 'value1',
            'one': 1
        }, level1.flattened)
        self.assertEqual({
            'first': 'value1',
            'one': 'one',
            'second': 'value2'
        }, level2.flattened)
        self.assertEqual({
            'first': 'value1',
            'one': 'one',
            'second': 'value two',
            'third': 'value3'
        }, level3.flattened)
