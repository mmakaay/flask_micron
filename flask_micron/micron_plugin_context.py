# -*- coding: utf-8 -*-
"""This module provides the MicronPluginContext class."""

class MicronPluginContext(object):
    """The MicronPluginContext is used to store the data that is required
    for Micron during request processing. This data is initialized by
    MicronMethod on every request and it is passed on to all MicronPlugin
    hooks.

    For information on the data that are stored in this object, take
    a look at :ref:`user_plugins_context`.
    """

    @property
    def config(self):
        return self._data.get('config', None)
    @config.setter
    def config(self, value):
        self._data['config'] = value

    @property
    def function(self):
        return self._data.get('function', None)
    @function.setter
    def function(self, value):
        self._data['function'] = value

    @property
    def input(self):
        return self._data.get('input', None)
    @input.setter
    def input(self, value):
        self._data['input'] = value

    @property
    def output(self):
        return self._data.get('output', None)
    @output.setter
    def output(self, value):
        self._data['output'] = value

    @property
    def error(self):
        return self._data.get('error', None)
    @error.setter
    def error(self, value):
        self._data['error'] = value

    @property
    def response(self):
        return self._data.get('response', None)
    @response.setter
    def response(self, value):
        self._data['response'] = value

    def __init__(self):
        self._data = {}

    def has(self, field):
        return field in self._data;
