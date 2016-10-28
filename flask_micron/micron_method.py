"""This module provides the MicronMethod class."""

import traceback
from functools import update_wrapper
import flask
from flask_micron.errors import MicronError
from flask_micron.errors import UnhandledException
from flask_micron.micron_method_config import MicronMethodConfig
from flask_micron.micron_plugin_context import MicronPluginContext


class MicronMethod(object):
    """The MicronMethod class wraps a standard function to make it work
    for Micron request handling. If forms the glue between the Flask
    app environment and Micron components.
    """
    def __init__(self, micron, function):
        """Creates a new Flask MicronMethod object.

        Args:
            micron: The Micron instance that creates this MicronMethod.
            function: The function to wrap this MicronMethod around.

        Example:

            from flask import Flask
            from flask_micron import Micron

            app = Flask(__name__)
            micron = Micron(app)

            # Using the API directly.
            method = MicronMethod(micron, lambda: 'Hello, world!')

            # Or (recommended) using the Micron method decorator.
            @micron.method()
            def hello():
                return 'Hello, world!'
        """
        update_wrapper(self, function)
        self.function = function
        self.plugins = micron.plugins
        self.config = MicronMethodConfig(micron.config)

    def configure(self, **configuration):
        """Updates the configuration for this MicronMethod instance.

        Args:
            **configuration: Configuration options that define in what way
                the Micron method must behave. These configuration options
                can be used to override the default configuration as set
                for the Micron object that was used to create this
                MicronMethod.

        Returns:
            The MicronMethod itself, useful for fluent syntax.

        Example:

            hello = lambda: 'Hello, world!'
            method = MicronMethod(micron, hello).configure(csrf=True)
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

        Returns:
            The Flask Response object to return to the client.
        """
        ctx = MicronPluginContext()
        ctx.config = self.config.flattened
        ctx.function = self.function
        try:
            self.plugins.call_all('start_request', ctx)
            self.plugins.call_all('check_access', ctx)
            self.plugins.call_all('after_check_access', ctx)
            self.plugins.call_one('read_input', ctx)
            self.plugins.call_all('process_input', ctx)
            self.plugins.call_one('call_function', ctx)
            self.plugins.call_all('process_output', ctx)
            self.plugins.call_one('create_response', ctx)
        except MicronError as error:
            self._handle_error(ctx, error)
        except Exception as error:
            self._handle_error(ctx, UnhandledException(error))
        finally:
            self.plugins.call_all('process_response', ctx)

        return ctx.response

    def _handle_error(self, ctx, error):
        ctx.error = error
        output = {}
        output['code'] = type(error).__name__
        output['caused_by'] = error.caused_by
        output['description'] = str(error)
        output['details'] = error.details
        output['trace'] = _get_trace(error)
        ctx.output = output
        self.plugins.call_one('create_response', ctx)
        self.plugins.call_all('process_error', ctx)


def _get_trace(error):
    """Returns a trace for the provided exception, in case the current
    app is running in debug mode.
    """
    ctx = flask._app_ctx_stack.top
    debug = ctx.app.debug if ctx else False
    if not debug:
        return None
    tb_list = traceback.extract_tb(error.__traceback__)
    return traceback.format_list(tb_list)
