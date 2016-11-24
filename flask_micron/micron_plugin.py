# -*- coding: utf-8 -*-
# pylint: disable=too-many-public-methods

"""This module provides the MicronPlugin class."""


class MicronPlugin(object):
    """The MicronPlugin defines the interface that can be implemented
    to create a Micron plugin. Derived classes can override methods
    to hook into specific phases of the request handling.

    For a detailed explanation on how to create Flask-Micron plugins,
    take a look at the :ref:`plugin documentation <user_plugins>`.
    """

    def request_methods(self, _):
        """This hook is called by Flask-Micron to retrieve a list of accepted
        request methods, used for creating the `Flask`_ routing entry.

        This hook does not receive a request context input parameter, because
        it is called at app initialization time and not within request context.

        :returns:
            A list of request methods (strings). These request methods
            must be valid input for the Flaks @app.route methods parameter.
        """

    def start_request(self, ctx):
        """A hook, called right at the start of the Micron request processing.
        This hook can be used to handle plugin initialization, e.g. applying
        default configuration options.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped as Micron method     |
        +--------------+---------------------------------------------------+
        | ctx.config   | The MicronMethodConfig, flattened as a dict       |
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
            from flask_micron import MicronPlugin

            class AddLocalTimeHeader(MicronPlugin):

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
        | ctx.function | The function that is wrapped as Micron method     |
        +--------------+---------------------------------------------------+
        | ctx.config   | The MicronMethodConfig, flattened as a dict       |
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
            from flask_micron import MicronPlugin
            from flask_micron import MicronClientError

            class NoServiceToday(MicronClientError):
                "This web service does not provide services today."

            class DayWatch(MicronPlugin):

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
        | ctx.function | The function that is wrapped as Micron method     |
        +--------------+---------------------------------------------------+
        | ctx.config   | The MicronMethodConfig, flattened as a dict       |
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
        into the input for the function that is wrapped as a Micron method.
        The hook must set the input property of the ctx object.

        Important:
        Since it makes sense to read input data only once, Micron will only
        call this hook for the last plugin that was registered that implements
        this hook.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped as Micron method     |
        +--------------+---------------------------------------------------+
        | ctx.config   | The MicronMethodConfig, flattened as a dict       |
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
        | ctx.function | The function that is wrapped as Micron method     |
        +--------------+---------------------------------------------------+
        | ctx.config   | The MicronMethodConfig, flattened as a dict       |
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
        | ctx.function | The function that is wrapped as Micron method     |
        +--------------+---------------------------------------------------+
        | ctx.config   | The MicronMethodConfig, flattened as a dict       |
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
        in the MicronPluginContext.

        Important:
        Since it makes sense to call the function only once, Micron will only
        call this hook for the last plugin that was registered that implements
        this hook.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped as Micron method     |
        +--------------+---------------------------------------------------+
        | ctx.config   | The MicronMethodConfig, flattened as a dict       |
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
        | ctx.function | The function that is wrapped as Micron method     |
        +--------------+---------------------------------------------------+
        | ctx.config   | The MicronMethodConfig, flattened as a dict       |
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
        client. This response must be stored in the MicronPluginContext.

        Important:
        Since it makes sense to create the response only once, Micron will only
        call this hook for the last plugin that was registered that implements
        this hook.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped as Micron method     |
        +--------------+---------------------------------------------------+
        | ctx.config   | The MicronMethodConfig, flattened as a dict       |
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
        | ctx.function | The function that is wrapped as Micron method     |
        +--------------+---------------------------------------------------+
        | ctx.config   | The MicronMethodConfig, flattened as a dict       |
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
            from flask_micron import MicronPlugin

            class UnderTheRug(MicronPlugin):
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
        | ctx.function | The function that is wrapped as Micron method     |
        +--------------+---------------------------------------------------+
        | ctx.config   | The MicronMethodConfig, flattened as a dict       |
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

            from flask_micron import MicronPlugin

            class ForceContextTypeTextPlain(MicronPlugin):

                def process_response(self, ctx):
                    ctx.response.content_type = 'text/plain'
        """

    def end_request(self, ctx):
        """A hook, called at the very end of the Micron request processing.
        This hook can be used to handle plugin teardown.

        +--------------+---------------------------------------------------+
        | ctx.function | The function that is wrapped as Micron method     |
        +--------------+---------------------------------------------------+
        | ctx.config   | The MicronMethodConfig, flattened as a dict       |
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
