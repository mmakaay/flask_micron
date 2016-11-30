# -*- coding: utf-8 -*-
# pylint: disable=too-many-public-methods
"""
flask_micron.plugin
===================

This module provides the classes that make up the Flask-Micron plugin system.

:copyright: (c) 2016 by Maurice Makaay
:license: BSD, see LICENSE for more details.
"""

import inspect


class Plugin(object):
    """The Plugin class defines the interface that can be implemented
    to create a Micron plugin. Derived classes can override methods
    to hook into specific phases of the request handling.

    For a detailed explanation on how to create Flask-Micron plugins,
    take a look at the :ref:`plugin documentation <user_plugins>`.
    """

    def start_request(self, ctx):
        """A hook, called right at the start of the Micron request processing.
        This hook can be used to handle plugin initialization, e.g. applying
        default configuration options.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped by Flask-Micron      |
        +--------------+---------------------------------------------------+
        | ctx.config   | The method config, flattened as a dict            |
        +--------------+---------------------------------------------------+
        | ctx.input    | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.output   | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.error    | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.response | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+

        Example plugin::

            from datetime import datetime
            import flask_micron

            class AddLocalTimeHeader(flask_micron.Plugin):

                def start_request(self, ctx):
                    ctx.config.setdefault('add_local_time_header', True)

                def process_response(self, ctx):
                    if ctx.config['add_local_time_header']:
                        local_time = datetime.now().isoformat()
                        ctx.response.headers['X-LocalTime'] = local_time

        Example use::

            from flask import Flask
            from flask_micron import Micron
            from your.package import AddLocalTimeHeader

            app = Flask(__name__)
            micron = Micron(app.plugin(AddLocalTimeHeader())

            @micron.method()
            def i_expose_local_time():
                return "Time teller"

            @micron.method(add_local_time_header = False)
            def i_do_not_expose_local_time():
                return "Time hider"
        """

    def check_access(self, ctx):
        """A hook for performing access control, called right after
        initializing the Micron request processing.

        When access is denied by a plugin, it should communicate this by
        raising an error that is derived from MicronClientError. The
        flask_micron.errors module already provides some useful error
        types (e.g. AccessDenied and AuthenticationRequired), but when
        no suitable error type is available, you can create your own.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped by Flask-Micron      |
        +--------------+---------------------------------------------------+
        | ctx.config   | The method config, flattened as a dict            |
        +--------------+---------------------------------------------------+
        | ctx.input    | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.output   | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.error    | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.response | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+

        Example plugin::

            from datetime import date
            import flask_micron

            class NoServiceToday(flask_micron.MicronClientError):
                "This web service does not provide services today."

            class DayWatch(flask_micron.Plugin):

                def check_access(self, ctx):
                    deny_day = ctx.config.get(deny_day, None)
                    if date.weekday(date.today()) == deny_day:
                        raise NoServiceToday("Closed when day=%d" % deny_day)

        Example use::

            from flask import Flask
            from flask_micron import Micron
            from your.package import DayWatch

            app = Flask(__name__)
            micron = Micron(app, deny_day=2).plugin(DayWatch())

            @micron.method(deny_day=0)
            def i_dont_like_mondays():
                return "Bob"

            @micron.method()
            def i_dont_like_wednesdays():
                return "Peter"
        """

    def after_check_access(self, ctx):
        """A hook called right after checking access and before Micron starts
        reading the input data from the request.

        An example use could be a keep-alive step for a session-based
        authentication system, to reset the session's expiry timer on
        every authenticated request (even when later on an error is
        returned).

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped by Flask-Micron      |
        +--------------+---------------------------------------------------+
        | ctx.config   | The method config, flattened as a dict            |
        +--------------+---------------------------------------------------+
        | ctx.input    | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.output   | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.error    | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.response | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        """

    def read_input(self, ctx):
        """A hook for reading data from the Flask request and translating it
        into the input for the function that is wrapped by Flask-Micron.
        The hook must set the input property of the ctx object.

        Important:
        Since it makes sense to read input data only once, Micron will only
        call this hook for the last plugin that was registered that implements
        this hook.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped by Flask-Micron      |
        +--------------+---------------------------------------------------+
        | ctx.config   | The method config, flattened as a dict            |
        +--------------+---------------------------------------------------+
        | ctx.input    | <MUST BE SET BY THIS HOOK>                        |
        +--------------+---------------------------------------------------+
        | ctx.output   | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.error    | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.response | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        """

    def normalize_input(self, ctx):
        """A hook to normalize the function input data.

        Called after reading the data from the request and deserializing
        it into input data for the function.

        The input data will be available in 'ctx.input' at this point.
        A plugin is allowed to modify the data or store new data in the
        'ctx.input' property.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped by Flask-Micron      |
        +--------------+---------------------------------------------------+
        | ctx.config   | The method config, flattened as a dict            |
        +--------------+---------------------------------------------------+
        | ctx.input    | The function input data (modifiable)              |
        +--------------+---------------------------------------------------+
        | ctx.output   | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.error    | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.response | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        """

    def validate_input(self, ctx):
        """A hook to validate the function input data.

        Called after the ``normalize_input`` hook, which takes care of
        normalizing the input data that is read from a request.

        The normalized input data will be available in 'ctx.input' at this
        point. A plugin is not supposed to modify the data.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped by Flask-Micron      |
        +--------------+---------------------------------------------------+
        | ctx.config   | The method config, flattened as a dict            |
        +--------------+---------------------------------------------------+
        | ctx.input    | The function input data                           |
        +--------------+---------------------------------------------------+
        | ctx.output   | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.error    | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.response | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        """

    def call_function(self, ctx):
        """A hook for calling the function that is wrapped as a Micron
        method. This is where the input data is passed to the function
        and where its return value must be stored as the output data
        in the plugin context.

        Important:
        Since it makes sense to call the function only once, Micron will only
        call this hook for the last plugin that was registered that implements
        this hook.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped by Flask-Micron      |
        +--------------+---------------------------------------------------+
        | ctx.config   | The method config, flattened as a dict            |
        +--------------+---------------------------------------------------+
        | ctx.input    | The function input data                           |
        +--------------+---------------------------------------------------+
        | ctx.output   | <MUST BE SET BY THIS HOOK>                        |
        +--------------+---------------------------------------------------+
        | ctx.error    | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.response | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        """

    def process_output(self, ctx):
        """A hook to post-process the output data.

        Called after executing the function that is wrapped as a Micron
        method. The return value from the function will be available in
        'ctx.output' at this point. A plugin is allowed to modify the data
        or store new data in the 'ctx.output' property.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped by Flask-Micron      |
        +--------------+---------------------------------------------------+
        | ctx.config   | The method config, flattened as a dict            |
        +--------------+---------------------------------------------------+
        | ctx.input    | The function input data                           |
        +--------------+---------------------------------------------------+
        | ctx.output   | The function output data (modifiable)             |
        +--------------+---------------------------------------------------+
        | ctx.error    | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        | ctx.response | <NOT AVAILABLE>                                   |
        +--------------+---------------------------------------------------+
        """

    def create_response(self, ctx):
        """A hook for creating the Flask Reponse object to return to the
        client. This response must be stored in the plugin context.

        Important:
        Since it makes sense to create the response only once, Micron will only
        call this hook for the last plugin that was registered that implements
        this hook.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped by Flask-Micron      |
        +--------------+---------------------------------------------------+
        | ctx.config   | The method config, flattened as a dict            |
        +--------------+---------------------------------------------------+
        | ctx.input    | The function input data                           |
        +--------------+---------------------------------------------------+
        | ctx.output   | The function output data (possibly empty in case  |
        |              | an exception was raised during the request)       |
        +--------------+---------------------------------------------------+
        | ctx.error    | The exception that was raised or None if no       |
        |              | exception was raised during the request           |
        +--------------+---------------------------------------------------+
        | ctx.response | <MUST BE SET BY THIS HOOK>                        |
        +--------------+---------------------------------------------------+
        """

    def process_error(self, ctx):
        """A hook to allow a plugin to act on errors (exception).

        Called after Micron has caught an error and has performed its
        own error processing, but before the process_response hook.

        The Flask (error) Response object will be available in 'ctx.response'
        at this point. A plugin is allowed to modify the response or store
        a completely new response in the 'ctx.response' property.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped by Flask-Micron      |
        +--------------+---------------------------------------------------+
        | ctx.config   | The method config, flattened as a dict            |
        +--------------+---------------------------------------------------+
        | ctx.input    | The function input data                           |
        +--------------+---------------------------------------------------+
        | ctx.output   | The function output data (possibly empty in case  |
        |              | an exception was raised during the request)       |
        +--------------+---------------------------------------------------+
        | ctx.error    | The exception that was raised                     |
        +--------------+---------------------------------------------------+
        | ctx.response | The Flask Response object                         |
        +--------------+---------------------------------------------------+

        Example::

            from flask import Response
            import flask_micron

            class UnderTheRug(flask_micron.Plugin):
                "When errors occur, deny them!"

                def process_error(self, ctx):
                    error_type = type(ctx.error).__name__,
                    ctx.response = Response(
                        "%s? Neh, that's a lie" % error_type
                        status=200)
        """

    def process_response(self, ctx):
        """A hook to allow a plugin to modify the response.

        Called at the very end of the MicronMethod request processing,
        possibly after handling (and creating a specific response for)
        an exception.

        The Flask Response object will be available in 'ctx.response'
        at this point. A plugin is allowed to modify the response
        or store a completely new Response object in the 'ctx.response'
        property.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped by Flask-Micron      |
        +--------------+---------------------------------------------------+
        | ctx.config   | The method config, flattened as a dict            |
        +--------------+---------------------------------------------------+
        | ctx.input    | The function input data                           |
        +--------------+---------------------------------------------------+
        | ctx.output   | The function output data                          |
        +--------------+---------------------------------------------------+
        | ctx.error    | The exception that was raised or None if no       |
        |              | exception was raised during the request           |
        +--------------+---------------------------------------------------+
        | ctx.response | The Flask Response object                         |
        +--------------+---------------------------------------------------+

        Example::

            import flask_micron

            class ForceContextTypeTextPlain(flask_micron.Plugin):

                def process_response(self, ctx):
                    ctx.response.content_type = 'text/plain'
        """

    def end_request(self, ctx):
        """A hook, called at the very end of the Micron request processing.
        This hook can be used to handle plugin teardown.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped by Flask-Micron      |
        +--------------+---------------------------------------------------+
        | ctx.config   | The method config, flattened as a dict            |
        +--------------+---------------------------------------------------+
        | ctx.input    | The function input data                           |
        +--------------+---------------------------------------------------+
        | ctx.output   | The function output data (possibly empty in case  |
        |              | an exception was raised during the request)       |
        +--------------+---------------------------------------------------+
        | ctx.error    | The exception that was raised or None if no       |
        |              | exception was raised during the request           |
        +--------------+---------------------------------------------------+
        | ctx.response | The Flask Response object                         |
        +--------------+---------------------------------------------------+
        """


class Container(object):
    """The Container class well... contains Flask-Micron plugins.
    It is used by Flask-Micron to register plugins and to execute hook
    functions from those plugins.
    """
    def __init__(self, *plugins):
        r"""Creates a new plugin Container object.

        :param \*plugins:
            Plugins to add to the container directly. Additional plugins can
            be added after construction using the method add(\*plugin)".
        """
        self._plugins = []
        self._hook_functions = {}
        self.add(*plugins)

    def add(self, *plugins):
        r"""Add Flask-Micron plugins to this Container.

        :param \*plugins:
            The plugin(s) to add.
        """
        for plugin in plugins:
            self._compile_plugin(plugin)
            self._plugins.append(plugin)

    def _compile_plugin(self, plugin):
        hooks = Compiler().compile(plugin)
        for hook, hook_function in hooks.items():
            self._hook_functions.setdefault(hook, []).append(hook_function)

    def call_all(self, context, hook):
        """Call the hook function in all registered plugins.

        :param flask_micron.plugin.Context context:
            The plugin context to pass to the plugins.
        :param string hook:
            The name of the hook function to call.
        """
        if hook in self._hook_functions:
            for hook_function in self._hook_functions[hook]:
                hook_function(context)

    def call_one(self, context, hook, monitor_field):
        """Call the hook function in all of the plugins, latest registered
        plugin first, until a plugin sets the monitor_field in the plugin
        context (Chain of Command pattern, the first plugin that handles
        the hook wins).

        :param flask_micron.plugin.Context context:
            The plugin context to pass to the plugins.
        :param string hook:
            The name of the hook function to call.
        :param string monitor_field:
            The name of the plugin context field to monitor. When a value
            is assigned to that field, no more hooks functions are called.
        """
        try:
            for hook_function in reversed(self._hook_functions[hook]):
                hook_function(context)
                if context.is_assigned(monitor_field):
                    return
        except KeyError:
            return None

    def __contains__(self, type_or_instance):
        """Checks if the plugin container contains a given plugin
        type or instance.

        Example::

            >>> import flask_micron
            >>> class MyPlugin(flask_micron.Plugin): pass
            >>> my = MyPlugin()
            >>> container = plugin.Container()
            >>> container.add(my)
            >>> my in container
            True
            >>> MyPlugin in container
            True
            >>> my2 = MyPlugin()
            >>> my2 in container
            False
        """
        if isinstance(type_or_instance, type):
            return any([
                p for p in self._plugins
                if isinstance(p, type_or_instance)
            ])
        else:
            return type_or_instance in self._plugins


class Compiler(object):
    """This class provides a compiler for Flask-Micron plugins.
    It inspects plugins and provides optimized code for calling
    the hook functions that are implemented by those plugins.
    """
    def compile(self, plugin):
        """Compiles the provided plugin.

        :param flask_micron.Plugin plugin:
            The plugin to compile.

        :returns:
            A dict of hooks that are implemented by the plugin.
            The keys are the hook names, the values are functions that
            can be called using a plugin context as argument.
        """
        functions = self._extract_functions(plugin)
        hook_functions = [
            (name, function)
            for name, function, base_function in functions
            for plugin_name, plugin_function in PLUGIN_METHODS.items()
            if name == plugin_name and base_function != plugin_function
        ]
        hooks = {}
        for name, hook_function in hook_functions:
            hooks[name] = self._create_hook_function_call(hook_function)
        return hooks

    def _extract_functions(self, plugin):
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

    def _create_hook_function_call(self, hook_function):
        def _call(context):
            return hook_function(context)
        return _call


PLUGIN_METHODS = dict((
    (name, base_function)
    for (name, base_function)
    in Plugin.__dict__.items()
    if name[0] != '_' and inspect.isfunction(base_function)
))


class Context(object):
    """The flask_micron.plugin.Context is used to store the data that is
    required for Micron during request processing. This data is initialized by
    MicronMethod on every request and it is passed on to all plugin hooks.

    For information on the data that are stored in this object, take
    a look at :ref:`user_plugins_context`.
    """

    @property
    def function(self):
        """The function that is wrapped as a MicronMethod."""
        return self._data.get('function', None)
    @function.setter
    def function(self, value):
        self._data['function'] = value

    @property
    def config(self):
        """The configuration for the MicronMethod, flattened as a dict.
        (see: :ref:`user_plugins_configurable`)
        """
        return self._data.get('config', None)
    @config.setter
    def config(self, value):
        self._data['config'] = value

    @property
    def input(self):
        """The input data for the function (the `Flask`_ ``Request``
        translated into a Python data structure).
        """
        return self._data.get('input', None)
    @input.setter
    def input(self, value):
        self._data['input'] = value

    @property
    def output(self):
        """The return value of the function."""
        return self._data.get('output', None)
    @output.setter
    def output(self, value):
        self._data['output'] = value

    @property
    def error(self):
        """The exception object, in case an unhandled exception is
        raised during the request handling.
        """
        return self._data.get('error', None)
    @error.setter
    def error(self, value):
        self._data['error'] = value

    @property
    def response(self):
        """The `Flask`_ ``Response`` object to return to the caller."""
        return self._data.get('response', None)
    @response.setter
    def response(self, value):
        self._data['response'] = value

    def __init__(self):
        self._data = {}

    def is_assigned(self, property_name):
        """Checks whether or not a value was actively assigned to
        a property.

        >>> ctx = Context()
        >>> ctx.input is None
        True
        >>> ctx.is_assigned('input')
        False
        >>> ctx.input = None
        >>> ctx.is_assigned('input')
        True

        :param string property_name:
            The name of the property to check.
        :returns:
            True if a value was assigned, False otherwise.
        """
        return property_name in self._data
