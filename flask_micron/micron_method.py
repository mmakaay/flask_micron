# -*- coding: utf-8 -*-
"""This module provides the MicronMethod class."""

import sys
import traceback
from functools import update_wrapper
import flask
from flask_micron.errors import MicronError
from flask_micron.errors import UnhandledException
from flask_micron.micron_plugin_context import MicronPluginContext
from flask_micron.micron_method_config import MicronMethodConfig


class MicronMethod(object):
    """The MicronMethod class wraps a standard function to make it work
    for Micron request handling. If forms the glue between the Flask
    app environment and Micron components.
    """
    def __init__(self, micron, function):
        """Creates a new Flask MicronMethod object.

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
        _enable_cookies_for_js_clients()
        ctx = MicronPluginContext()
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

    def _handle_error(self, ctx, error, traceback_):
        ctx.error = error
        ctx.output = {
            'code': type(error).__name__,
            'caused_by': error.caused_by,
            'description': str(error),
            'details': error.details,
            'trace': _create_trace(traceback_)
        }
        self.plugins.call_one(ctx, 'create_response', 'reponse')
        self.plugins.call_all(ctx, 'process_error')
        self.plugins.call_all(ctx, 'process_response')
        self.plugins.call_all(ctx, 'end_request')


def _enable_cookies_for_js_clients():
    flask.current_app.config['SESSION_COOKIE_HTTPONLY'] = False


def _create_trace(traceback_):
    ctx = flask._app_ctx_stack.top
    debug = ctx.app.debug if ctx else False
    if not debug:
        return None
    tb_list = traceback.extract_tb(traceback_)
    formatted = traceback.format_list(tb_list)
    stripped = [line.strip() for line in formatted]
    return stripped
