"""This module provides the MicronPluginCompiler class."""

import inspect
from flask_micron.micron_plugin import MicronPlugin


class MicronPluginCompiler(object):
    """The MicronPluginCompiler class is used to inspect Micron plugins
    and provide optimized code for calling the hook functions that
    are implemented by those plugins.
    """
    def compile(self, plugin):
        """Compiles the provided plugin.

        Returns:
           A dict of hooks that are implemented by the plugin.
           The keys are the hook names, the values are functions that
           can be run using a MicronPluginContext as input and which
           will automatically call the hook function from the plugin.
        """
        hooks = _compile_hooks(plugin)
        return hooks


def _compile_hooks(plugin):
    functions = _extract_functions(plugin)
    hook_functions = [
        (name, function)
        for name, function, base_function in functions
        for plugin_name, plugin_function in PLUGIN_METHODS.items()
        if name == plugin_name and base_function != plugin_function
    ]
    hooks = {}
    for name, hook_function in hook_functions:
        hooks[name] = _create_hook_function_call(hook_function)
    return hooks


def _create_hook_function_call(hook_function):
    def _call(context):
        hook_function(context)
    return _call


def _extract_functions(plugin):
    if isinstance(plugin, dict):
        functions = [
            (n, f, f) for n, f in plugin.items()
            if inspect.isfunction(f)
        ]
    else:
        functions = [
            (name, method, method.__func__) for name, method
            in inspect.getmembers(plugin, inspect.ismethod)
        ] + [
            (name, function, function) for name, function
            in inspect.getmembers(plugin, inspect.isfunction)
        ]
    return functions


PLUGIN_METHODS = dict((
    (name, base_function)
    for (name, base_function)
    in MicronPlugin.__dict__.items()
    if name[0] != '_' and inspect.isfunction(base_function)
))
