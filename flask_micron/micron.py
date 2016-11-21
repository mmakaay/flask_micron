"""This module provides the Micron class."""
# TODO deal correctly with unicode in all places, Werkzeug should be
# using unicode, not bytes as it is now in the Response.data.

from flask_micron.errors import ImplementationError
from flask_micron.micron_method import MicronMethod
from flask_micron.micron_plugin_container import MicronPluginContainer
from flask_micron.micron_plugin_context import MicronPluginContext
from flask_micron.micron_method_config import MicronMethodConfig
from flask_micron.plugins import csrf
from flask_micron.plugins import json_input
from flask_micron.plugins import normalize_input
from flask_micron.plugins import call_function
from flask_micron.plugins import json_output


class Micron(object):
    """The Micron class is used to decorate regular functions, to become all
    singing and all dancing :class:`Micron methods
    <flask_micron.micron_method.MicronMethod>`, which are plugged into the
    routing of a Flask application.
    """
    def __init__(self, app=None, **configuration):
        """
        :param Flask app:
            The Flask app (or Blueprint) to wrap.
        :param **configuration:
            Configuration options that define in what way Micron methods that
            are created using this Micron instance must behave.  These
            configuration options can be overridden by method-specific
            configuration options, defined in the ``@micron.method()``
            decorator.

        Example::

            from flask import Flask
            from flask_micron import Micron

            app = Flask(__name__)
            micron = Micron(app, csrf=True)

            @micron.method()
            def hello():
                return "Hello, world!"
        """
        self.config = MicronMethodConfig(**configuration)

        self.plugins = MicronPluginContainer(
            csrf.Plugin(),
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
        self._add_ping_method()

    def _add_ping_method(self):
        """The ping method is provided as a standard means for clients to
        bootstrap the CSRF protection schema. In this implementation, as
        little as possible is done to provide the client with a fresh
        CSRF token when POSTing to /ping.
        """
        @self.app.route('/ping', methods=['POST'])
        def _ping():
            ctx = MicronPluginContext()
            ctx.output = 'pong'
            self.plugins.call_one(ctx, 'create_response')
            csrf.Plugin().process_response(ctx)
            return ctx.response

    def plugin(self, plugin):
        """Adds a :class:`MicronPlugin <flask_micron.MicronPlugin>` to this
        Micron object. See :ref:`user_plugins` for information on writing
        and using plugins.

        :param MicronPlugin plugin:
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
        self.plugins.add(plugin)
        return self

    def configure(self, **configuration):
        """Updates the configuration for this Micron instance.

        :param **configuration:
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
            micron = Micron(app).configure(csrf=False)

        Note: the last line is equivalent to::

            micron = Micron(app, csrf=False)
        """
        self.config.configure(**configuration)
        return self

    def method(self, rule=None, **configuration):
        """Decorates a function to make it work as a Micron method.

        :param string rule:
            The URL rule to use for this method. Default value:
            "/<name of decorated function>"
        :param **configuration:
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
            micron = Micron(app, csrf=True)

            @micron.method(csrf=False)
            def hello(who="World"):
                return "Hello, %s" % who
        """
        if self.app is None:
            raise ImplementationError(
                'The @micron.method decorator can only be used when '
                'the Micron class is linked to a Flask app')

        def _decorator(func, rule=rule):
            if rule is None:
                rule = _create_url_rule(func)
            method = MicronMethod(self, func).configure(**configuration)
            self.app.add_url_rule(rule, view_func=method, methods=['POST'])
            return func
        return _decorator


def _create_url_rule(micron_method):
    """Creates the URL rule for a Micron method.

    :param MicronMethod micron_method:
        The MicronMethod to create the route for.

    :returns:
        The URL rule: "/<function name>"
    """
    name = micron_method.__name__.split('.')[-1]
    return '/' + name
