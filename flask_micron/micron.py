# -*- coding: utf-8 -*-
"""
flask_micron.micron
===================

This module provides the Micron class, which is used to decorate
a function to make it work as a :any:`MicronMethod`.

:copyright: (c) 2016 by Maurice Makaay
:license: BSD, see LICENSE for more details.
"""

from flask_micron.errors import ImplementationError
from flask_micron.method import MicronMethod
from flask_micron.method import MicronMethodConfig
from flask_micron import plugin
from flask_micron.plugins import json_input
from flask_micron.plugins import normalize_input
from flask_micron.plugins import call_function
from flask_micron.plugins import json_output


class Micron(object):
    """Used to decorate a regular function, to become an all singing and all
    dancing :any:`MicronMethod`, which is plugged into the routing of a
    `Flask`_ application.
    """

    def __init__(self, app=None, **configuration):
        r"""
        :param Flask app:
            The Flask app (or Blueprint) to wrap.
        :param \**configuration:
            Configuration options that define in what way a :any:`MicronMethod`
            that is created using this Micron instance must behave. These
            configuration options can be overridden by method-specific
            configuration options, defined in the ``@micron.method()``
            decorator.

        Example::

            from flask import Flask
            from flask_micron import Micron

            app = Flask(__name__)
            micron = Micron(app)

            @micron.method()
            def hello():
                return "Hello, world!"
        """
        self.config = MicronMethodConfig(**configuration)

        self.plugins = plugin.Container(
            json_input.Plugin(),
            normalize_input.Plugin(),
            call_function.Plugin(),
            json_output.Plugin()
        )

        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initializes a Flask app as a Micron app.

        :param Flask app:
            The Flask app to initialize Micron for.

        Example::

            from flask import Flask
            from flask_micron import Micron

            micron = Micron()
            app = Flask(__name__)
            micron.init_app(app)
        """
        self.app = app

    def plugin(self, plugin_object):
        """Adds a :class:`Plugin <flask_micron.Plugin>` to this
        Micron object. See :ref:`user_plugins` for information on writing
        and using plugins.

        :param flask_micron.Plugin plugin_object:
            The plugin to add to this Micron object.

        :returns:
            This Micron instance, useful for fluent syntax.

        Example::

            from flask import Flask
            from flask_micron import Micron
            import my_stuff

            app = Flask(__name__)
            micron = Micron(app)

            my_plugin = my_stuff.Plugin()
            micron.plugin(my_plugin)
        """
        self.plugins.add(plugin_object)
        return self

    def configure(self, **configuration):
        r"""Updates the configuration for this Micron instance.

        :param \**configuration:
            Configuration options that define in what way Micron methods that
            are created using this Micron instance must behave. These
            configuration options can be overridden by method-specific
            configuration options, defined in the @micron.method(...)
            decorator.

        :returns:
            This Micron instance, useful for fluent syntax.

        Example::

            from flask import Flask
            from flask_micron import Micron

            app = Flask(__name__)
            micron = Micron(app).configure(option_name=some_value)

        Note: the last line is equivalent to::

            micron = Micron(app, option_name=some_value)
        """
        self.config.configure(**configuration)
        return self

    def method(self, rule=None, **configuration):
        r"""Decorates a function to make it work as a Micron method.

        :param string rule:
            The URL rule to use for this method. Default value:
            /<name of decorated function>
        :param \**configuration:
            Configuration options that define in what way the Micron method
            must behave. These configuration options can be used to override
            the default configuration as set for the Micron object.

        :returns:
            A decorator that will take care of embedding the Micron method
            in the Flask application and hooking it up with the Micron
            request handling.

        Example::

            from flask import Flask
            from flask_micron import Micron

            app = Flask(__name__)
            micron = Micron(app, x="default config value")

            @micron.method(x="function-specific config value")
            def hello(who='World'):
                return 'Hello, %s' % who
        """
        if self.app is None:
            raise ImplementationError(
                'The @micron.method decorator can only be used when '
                'the Micron class is linked to a Flask app')

        def _decorator(func, rule=rule):
            if rule is None:
                rule = _create_url_rule(func)
            wrapped = MicronMethod(self, func).configure(**configuration)
            self.app.add_url_rule(rule, view_func=wrapped, methods=['POST'])
            return func
        return _decorator

def _create_url_rule(func):
    """Creates the URL rule for a function.

    :param function func:
        The MicronMethod to create the route for.

    :returns:
        The URL rule: "/<function name>"
    """
    name = func.__name__.split('.')[-1]
    return '/' + name
