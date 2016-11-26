# -*- coding: utf-8 -*-
from flask_micron.errors import ImplementationError
from flask_micron import plugin
from flask_micron.plugins.call_function import MissingInput
from flask_micron.plugins.call_function import UnexpectedInput
from flask_micron.plugins.call_function import Plugin
from tests import MicronTestCase


class Tests(MicronTestCase):

    def test_InputNone_NoArgFunction_OK(self):
        self.assertEqual(True, _call_plugin(func_noargs, None))

    def test_InputNotNone_NoArgFunction_NotOK(self):
        with self.assertRaises(UnexpectedInput):
            _call_plugin(func_noargs, False)

    def test_InputNotNone_NoArgFunction_OK(self):
        self.assertEqual(False, _call_plugin(func_onearg, False))

    def test_InputNone_OneArgFunction_NotOK(self):
        with self.assertRaises(MissingInput):
            _call_plugin(func_onearg, None)

    def test_InputNone_OneArgWithDefaultFunction_OK(self):
        self.assertEqual(True, _call_plugin(func_oneargwithdefault, None))

    def test_InputNotNone_OneArgWithDefaultFunction_OK(self):
        self.assertEqual(False, _call_plugin(func_oneargwithdefault, False))

    def test_MultipleArgsFunction_NotOK(self):
        with self.assertRaises(ImplementationError):
            _call_plugin(func_multipleargs, None)

    def test_integration(self):
        # The 'call_function' plugin is loaded by default by Micron,
        # so we only need to setup a test method here.
        @self.micron.method(csrf=False)
        def echo(arg):
            return arg

        response = self.request('/echo', 'well ..well ..ell ..ll ..')
        self.assertEqual('well ..well ..ell ..ll ..', response.output)


def _call_plugin(function, arg):
    ctx = plugin.Context()
    ctx.input = arg
    ctx.function = function
    Plugin().call_function(ctx)
    return ctx.output


def func_noargs():
    return True


def func_onearg(arg1):
    return arg1


def func_oneargwithdefault(arg1=True):
    return arg1


def func_multipleargs(arg1, arg2):
    return (arg1, arg2)
