# -*- coding: utf-8 -*-
"""
flask_micron.method
===================

This module provides the functionality for wrapping functions to
make them work for Flask-Micron request handling.  

:copyright: (c) 2016 by Maurice Makaay
:license: BSD, see LICENSE for more details.
"""

import re
import sys
import traceback
from functools import update_wrapper
import flask
from flask_micron import plugin
from flask_micron.errors import MicronError
from flask_micron.errors import UnhandledException
from flask_micron.errors import ImplementationError


class MicronMethod(object):
    """The MicronMethod class wraps a standard function to make it work
    for Flask-Micron request handling. If forms the glue between the
    `Flask`_ app environment and Flask-Micron components.
    """

    def __init__(self, micron, function):
        """Creates a new MicronMethod object.

        :param Micron micron:
            The Micron instance that creates this MicronMethod.
        :param function function:
            The function to wrap this MicronMethod around.
        """
        update_wrapper(self, function)
        self.function = function
        self.plugins = micron.plugins
        self.config = MicronMethodConfig(micron.config)

    def configure(self, **configuration):
        r"""Updates the configuration for this MicronMethod instance.

        :param \**configuration:
            Configuration options that define in what way the Micron method
            must behave. These configuration options can be used to override
            the default configuration as set for the Micron object that was
            used to create this MicronMethod.

        :returns:
            The MicronMethod itself, useful for fluent syntax.
        """
        self.config.configure(**configuration)
        return self

    def __call__(self):
        """Executes the MicronMethod.

        This method implements the very core of Micron request handling.
        Micron lets Flask take care of web server interaction, routing,
        context setup, etc. Flask will eventually call this method to
        render the route. That is when the Micron-specific request
        handling kicks in.

        :returns:
            The Flask Response object to return to the client.
        """
        self._enable_cookies_for_js_clients()
        ctx = plugin.Context()
        ctx.config = self.config.flattened
        ctx.function = self.function
        try:
            self.plugins.call_all(ctx, 'start_request')
            self.plugins.call_all(ctx, 'check_access')
            self.plugins.call_all(ctx, 'after_check_access')
            self.plugins.call_one(ctx, 'read_input', 'input')
            self.plugins.call_all(ctx, 'normalize_input')
            self.plugins.call_all(ctx, 'validate_input')
            self.plugins.call_one(ctx, 'call_function', 'output')
            self.plugins.call_all(ctx, 'process_output')
            self.plugins.call_one(ctx, 'create_response', 'response')
            self.plugins.call_all(ctx, 'process_response')
            self.plugins.call_all(ctx, 'end_request')
        except MicronError:
            (_, error, traceback_) = sys.exc_info()
            self._handle_error(ctx, error, traceback_)
        except Exception:
            (_, error, traceback_) = sys.exc_info()
            self._handle_error(ctx, UnhandledException(error), traceback_)

        return ctx.response

    def _enable_cookies_for_js_clients(self):
        flask.current_app.config['SESSION_COOKIE_HTTPONLY'] = False

    def _handle_error(self, ctx, error, traceback_):
        ctx.error = error
        ctx.output = {
            'code': type(error).__name__,
            'caused_by': error.caused_by,
            'description': str(error),
            'details': error.details,
            'trace': self._create_trace(traceback_)
        }
        self.plugins.call_one(ctx, 'create_response', 'reponse')
        self.plugins.call_all(ctx, 'process_error')
        self.plugins.call_all(ctx, 'process_response')
        self.plugins.call_all(ctx, 'end_request')

    def _create_trace(self, traceback_):
        ctx = flask._app_ctx_stack.top
        debug = ctx.app.debug if ctx else False
        if not debug:
            return None
        tb_list = traceback.extract_tb(traceback_)
        formatted = traceback.format_list(tb_list)
        stripped = [line.strip() for line in formatted]
        return stripped


class MicronMethodConfig(object):
    """This class encapsulates the configuration options that are used
    for executing a MicronMethod.

    Within Flask-Micron, this configuration is performed at two levels:
    * The Micron-level configuration (defined by calling the method
      Micron.configure() on a Micron instance)
    * The MicronMethod-level configuration (defined by options that were
      used in the @micron.method() decorator)

    This class supports this multi-level configuration by making each
    MicronMethodConfig aware of its parent configuration (so basically,
    we create a linked list of configurations).

    Example:

        >>> level1 = MicronMethodConfig(x=False, y=True)
        >>> level2 = MicronMethodConfig(level2, x=True, y=True)
        >>> level3 = MicronMethodConfig(level3, y=None)
        >>> level1.x
        False
        >>> level2.x
        True
        >>> level3.x
        True
        >>> level2.y
        True
        >>> level3.y
        None
    """

    IDENTIFIER_FORMAT = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')

    def __init__(self, parent=None, **configuration):
        r"""Creates a new MicronMethodConfig.

        :param MicronMethodConfig parent:
            The parent of this MicronMethodConfig object.
        :param \**configuration:
            Values to instantiate this config object with.
        """
        # Using the super __setattr__ is required to prevent endless loops,
        # since we implemented __setattr__/__getattr__ for this class.
        setmyattr = super(MicronMethodConfig, self).__setattr__
        setmyattr('_parent', parent)
        setmyattr('_data', {})

        self.configure(**configuration)

    def __call__(self, **configuration):
        return self.configure(**configuration)

    def configure(self, **configuration):
        r"""Set configuration values for this config object.

        :param \**configuration:
            Values to update this config object with.

        :returns:
            The MicronMethodConfig itself, useful for fluent syntax.
        """
        for name, value in configuration.items():
            self.set(name, value)
        return self

    def __getattr__(self, name):
        """For making config options available as instance attributes
        of the config object.
        """
        return self.get(name)

    def __setattr__(self, name, value):
        """For making config options available as instance attributes
        of the config object.
        """
        self.set(name, value)

    def set(self, name, value):
        """Set a configuration option by name.

        :param string name:
            The name of the configuration option.
        :param value:
            The value to set it to.
        """
        self._check_option_name(name)
        self._data[name] = value

    def _check_option_name(self, name):
        if not self.IDENTIFIER_FORMAT.match(name):
            raise ImplementationError(
                "Invalid configuration option name '%s' used "
                "(only lowercase letters, numbers and underscores are allowed "
                "and the name must start with a letter)" % name)

    @property
    def option_names(self):
        """Returns a set of all configuration option names that are currently
        in use in the MicronMethodConfig hierarchy.
        """
        names = set()
        parent = self
        while parent is not None:
            names.update(parent._data.keys())
            parent = parent._parent
        return names

    @property
    def flattened(self):
        """Returns a dict of all configuration options that are currently
        in use in the MicronMethodConfig hierarchy.

        :returns:
            A dict, containing all configuration options.
        """
        flattened = dict(self._data)
        parent = self._parent
        while parent:
            for name, value in parent._data.items():
                flattened.setdefault(name, value)
            parent = parent._parent
        return flattened


    def get(self, name):
        """Retrieve a configuration value by name.

        When this MicronMethodConfig object does not have a value for the
        requested configuration option, then the parent config will be
        consulted. When no parent config exists, a KeyError is raised.

        :param string name:
            The name of the configuration value to retrieve.

        :returns:
            The configuration value.
        """
        if name in self._data:
            return self._data[name]
        if self._parent is None:
            raise KeyError(
                "No value defined for configuration option '%s'" % name)
        return self._parent.get(name)
