"""This module provides the MicronPlugin class."""


class MicronPlugin(object):
    """The MicronPlugin provides an interface that can be implemented
    to create a Micron plugin.

    The MicronPlugin base class contains methods with can be overridden in
    order to hook into specific phases of the request handling. This plugin
    mechanism could for example be used for implementing authentication,
    authorization, ACL checking and mangling of input and output data,
    but anything is possible.


    Duck Typing
    -----------

    It is not strictly required to derive from MicronPlugin in order
    to create a plugin. In the tradition of Python, Duck Typing is
    allowed, meaning that you can register any object as a plugin,
    as long as it provides plugin hook functions.

    In fact, Micron goes even a step further by accepting
    non-MicronPlugin objects that implement only a subset of the
    plugin hook functions ("Crippled Duck Typing"?).


    Available hooks
    ---------------

    These are the available hook functions, in the order in which
    they are called by Micron during request processing:

        - start_request(self, ctx)
        - check_access(self, ctx)
        - after_check_access(self, ctx)
        - read_input(self, ctx) *
        - process_input(self, ctx)
        - call_function(self, ctx) *
        - process_output(self, ctx)
        - create_response(self, ctx) *
        - process_error(self, ctx)
        - process_response(self, ctx)

        *) A special type of hook, for which only the last registered
           plugin that implements the hook is called.

    MicronPluginContext
    -------------------

    To keep things straight forward, every hook function receives the
    same input object: a MicronPluginContext. This object contains
    data that is used by plugins during request processing.

    At the start of the request, the context object is empty, but during
    request handling, the data is enriched with new data, as soon as it
    comes available.

    For more information on the available data in the context,
    see the documentation for each of the hook functions.


    Plugin behavior configuration
    -----------------------------

    In case your plugin can display different kinds of behavior, and
    you need to be able to differentiate the behavior per Micron method,
    then you can make use of the Micron configuration handling.

    Configuration can be performed at two levels:
    1. The Micron object
    2. The @micron.method() decorator

    The Micron object configuration is used for all functions that are
    decorated using that object. The decorator configuration can be
    used to override the configuration per decorated function.
    Here's an example:

        app = Flask(__name__)
        micron = Micron(app, configA='plug', configB='in')

        @micron.method(configA='drive')
        def hello():
            return "Hello, world!"

        @micron.method(configC='peep')
        def bye():
            return "Bye, world!"

    When Micron processes a request, it will aggregate the configuration
    options for the called Micron method into a single dict and pass
    it to plugin hook functions via the MicronPluginContext. For the above
    example, you would see the following configuration data in a plugin:

        hello()  ctx.config = {
                     "configA": "drive",
                     "configB": "in"
                 }

        bye()    ctx.config = {
                     "configA": "plug",
                     "configB": "in",
                     "configC": "peep"
                 }

    Here's an example of how you could access these configuration options
    from within a hook function, and fall back to a default value when
    a configuration option is not defined in Micron and the Micron method:

        def process_input(self, ctx):
            ctx.input.things = [
                ctx.config.get('configA', 'defaultA'),
                ctx.config.get('configB', 'defaultB'),
                ctx.config.get('configC', 'defaultC')
            ]

    Another way to work with default values, could be to resolve the default
    values in the start_request hook function, so other hook functions can
    be assured that a configuration value is set:

        def start_request(self, ctx):
            ctx.config.setdefault('configA', 'defaultA')
            ctx.config.setdefault('configB', 'defaultB')
            ctx.config.setdefault('configC', 'defaultC')

        def process_input(self, ctx):
            ctx.input.things = [
                ctx.config['configA'],
                ctx.config['configB'],
                ctx.config['configC']
            ]

    Beware that the configuration space is shared by all plugins. So use
    configuration option names that are not likely to collide with other
    plugins.


    Example
    -------

    Here an example of a (rather useless) MicronPlugin, used for guarding
    access to Micron methods:

        from flask_micron import MicronPlugin
        from flask_micron.errors import AccessDenied

        class Plugin(MicronPlugin):

            def check_access(self, ctx):
                if ctx.config.get(guard, True):
                    raise AccessDenied("Access denied by StupidGuard")

    And to use the plugin in the service code:

        from flask import Flask
        from flask_micron import Micron
        from your.package import guard

        app = Flask(__name__)
        micron = Micron(app).plugin(guard.Plugin())

        @micron.method(guard=True)
        def guarded():
            return "I am guarded"

        @micron.method()
        def guarded_by_default():
            return "I am guarded by default"

        @micron.method(guard=False)
        def not_guarded():
            return "I am not guarded"
    """

    def start_request(self, ctx):
        """A hook, called right at the start of the Micron request processing.

        Args:
            ctx: The MicronPluginContext, describing the current request.
            ctx.function : The function that is wrapped as Micron method
            ctx.config   : The MicronMethodConfig, flattened as a dict
            ctx.input    : <NOT AVAILABLE>
            ctx.output   : <NOT AVAILABLE>
            ctx.error    : <NOT AVAILABLE>
            ctx.response : <NOT AVAILABLE>

        Example (Crippled Duck Typing style):

            class ClosedDownForMaintenance(MicronServerError):
                "The service is shut down completely, for maintenance purposes."

            class MaintenanceMode:
                def start_request(self, ctx):
                    if (ctx.config.get("maintenance", False))
                        raise ClosedDownForMaintenance()

            --------

            from flask import Flask
            from flask_micron import Micron
            from your.package import ClosedDownForMaintenance

            app = Flask(__name__)
            micron = Micron(app).plugin(ClosedDownForMaintenance())
            micron.configure(maintenance=True)

            @micron.method()
            def in_maintenance_by_default():
                return "Hello, me!"

            @micron.method(maintenance=True)
            def explicitly_in_maintenance():
                return "Hello, you!"

            @micron.method(maintenance=False)
            def not_in_maintenance():
                return "Hello, people!"
        """

    def check_access(self, ctx):
        """A hook for performing access control, called right after
        initializing the Micron request processing.

        When access is denied by a plugin, it should communicate this by
        raising an error that is derived from MicronClientError. The
        flask_micron.errors module already provides some useful error
        types (e.g. AccessDenied and AuthenticationRequired), but when
        no suitable error type is available, you can create your own.

        Args:
            ctx: The MicronPluginContext, describing the current request.
            ctx.function : The function that is wrapped as Micron method
            ctx.config   : The MicronMethodConfig, flattened as a dict
            ctx.input    : <NOT AVAILABLE>
            ctx.output   : <NOT AVAILABLE>
            ctx.error    : <NOT AVAILABLE>
            ctx.response : <NOT AVAILABLE>

        Example:

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

            --------

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

        Args:
            ctx: The MicronPluginContext, describing the current request.
            ctx.function : The function that is wrapped as Micron method
            ctx.config   : The MicronMethodConfig, flattened as a dict
            ctx.input    : <NOT AVAILABLE>
            ctx.output   : <NOT AVAILABLE>
            ctx.error    : <NOT AVAILABLE>
            ctx.response : <NOT AVAILABLE>
        """

    def read_input(self, ctx):
        """A hook for reading data from the Flask request and translating it
        into the input for the function that is wrapped as a Micron method.
        The hook must set the input property of the ctx object.

        Important:
        Since it makes sense to read input data only once, Micron will only
        call this hook for the last plugin that was registered that implements
        this hook.

        Args:
            ctx: The MicronPluginContext, describing the current request.
            ctx.function : The function that is wrapped as Micron method
            ctx.config   : The MicronMethodConfig, flattened as a dict
            ctx.input    : <NOT AVAILABLE> <- set by this hook
            ctx.output   : <NOT AVAILABLE>
            ctx.error    : <NOT AVAILABLE>
            ctx.response : <NOT AVAILABLE>
        """

    def process_input(self, ctx):
        """A hook to modify the function input data.

        Called after reading the data from the request and deserializing
        it into input data for the function.

        The input data will be available in 'ctx.input' at this point.
        A plugin is allowed to modify the data or store new data in the
        'ctx.input' property.

        Args:
            ctx: The MicronPluginContext, describing the current request.
            ctx.function : The function that is wrapped as Micron method
            ctx.config   : The MicronMethodConfig, flattened as a dict
            ctx.input    : The function input data <- new for this hook
            ctx.output   : <NOT AVAILABLE>
            ctx.error    : <NOT AVAILABLE>
            ctx.response : <NOT AVAILABLE>
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

        Args:
            ctx: The MicronPluginContext, describing the current request.
            ctx.function : The function that is wrapped as Micron method
            ctx.config   : The MicronMethodConfig, flattened as a dict
            ctx.input    : The function input data
            ctx.output   : <NOT AVAILABLE> <- set by this hook
            ctx.error    : <NOT AVAILABLE>
            ctx.response : <NOT AVAILABLE>
        """

    def process_output(self, ctx):
        """A hook to modify the request output data.

        Called after executing the function that is wrapped as a Micron method
        and serializing its output data into a JSON response.

        The return value from the function will be available in 'ctx.output'
        at this point. A plugin is allowed to modify the data or store new
        data in the 'ctx.output' property.

        Args:
            ctx: The MicronPluginContext, describing the current request.
            ctx.function : The function that is wrapped as Micron method
            ctx.config   : The MicronMethodConfig, flattened as a dict
            ctx.input    : The function input data
            ctx.output   : The function output data <- new for this hook
            ctx.error    : <NOT AVAILABLE>
            ctx.response : <NOT AVAILABLE>

        Args:
            ctx: The MicronPluginContext, describing the current request.
        """

    def create_response(self, ctx):
        """A hook for creating the Flask Reponse object to return to the
        client. This response must be stored in the MicronPluginContext.

        Important:
        Since it makes sense to create the response only once, Micron will only
        call this hook for the last plugin that was registered that implements
        this hook.

        Args:
            ctx: The MicronPluginContext, describing the current request.
            ctx.function : The function that is wrapped as Micron method
            ctx.config   : The MicronMethodConfig, flattened as a dict
            ctx.input    : The function input data
            ctx.output   : The function output data (possibly empty)
            ctx.error    : The exception that was raised if any, otherwise None
            ctx.response : <NOT AVAILABLE> <- set by this hook
        """

    def process_error(self, ctx):
        """A hook to allow a plugin to act on errors (exception).

        Called after Micron has caught an error and has performed its
        own error processing, but before the process_response hook.

        The Flask (error) Response object will be available in 'ctx.response'
        at this point. A plugin is allowed to modify the response or store
        a completely new response in the 'ctx.response' property.

        Args:
            ctx: The MicronPluginContext, describing the current request.
            ctx.function : The function that is wrapped as Micron method
            ctx.config   : The MicronMethodConfig, flattened as a dict
            ctx.input    : The function input data (possibly empty)
            ctx.output   : The function output data (possibly empty)
            ctx.error    : The exception that was raised
            ctx.response : The Flask response object <- new for this hook

        Example:

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

        Args:
            ctx: The MicronPluginContext, describing the current request.
            ctx.function : The function that is wrapped as Micron method
            ctx.config   : The MicronMethodConfig, flattened as a dict
            ctx.input    : The function input data
            ctx.output   : The function output data
            ctx.error    : <NOT AVAILABLE>
            ctx.response : The Flask response object <- new for this hook

        Example:

            from flask_micron import MicronPlugin

            class ForceContextTypeTextPlain(MicronPlugin):

                def process_response(self, ctx):
                    ctx.response.content_type = 'text/html'
        """
