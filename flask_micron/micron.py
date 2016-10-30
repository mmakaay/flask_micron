"""This module provides the Micron class."""
# TODO deal correctly with unicode in all places, Werkzeug should be using unicode, not bytes as it is now in the Response.data.

from flask_micron.errors import ImplementationError
from flask_micron.micron_method import MicronMethod
from flask_micron.micron_plugin_container import MicronPluginContainer
from flask_micron.micron_method_config import MicronMethodConfig
from flask_micron.plugins import csrf
from flask_micron.plugins import json_input
from flask_micron.plugins import normalize_input
from flask_micron.plugins import call_function
from flask_micron.plugins import json_output


class Micron(object):
    """The Micron class is used to decorate regular functions, to become
    all singing and all dancing MicronMethods, which are plugged into
    the routing of a Flask application.

    Example:

        from flask import Flask
        from flask_micron import Micron

        app = Flask(__name__)
        micron = Micron(app, csrf=True)

        @micron.method()
        def hello():
                return "Hello, world!"
    """
    def __init__(self, app=None, **configuration):
        """Creates a new Micron object.

        Args:
            app: The Flask app (or Blueprint) to wrap.
            **configuration: Configuration options that define in what way
                Micron methods that are created using this Micron instance
                must behave. These configuration options can be overridden
                by method-specific configuration options, defined in the
                @micron.method(...) decorator.

        Example:

            from flask import Flask
            from flask_micron import Micron

            app = Flask(__name__)
            micron = Micron(app, csrf=True)
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

        Args:
            app: The Flask app to initialize Micron for.

        Example:

            from flask import Flask
            from flask_micron import Micron

            micron = Micron()
            app = Flask(__name__)
            micron.init_app(app)
        """
        self.app = app
        self._add_ping_method(app)

    def _add_ping_method(self, app):
        """Add /ping as a Micron method to the app."""
        @self.method(csrf=False)
        def ping():
            return 'pong'

    def plugin(self, plugin):
        """Adds a MicronPlugin to this Micron object.
        See the documentation for MicronPlugin for more information on
        writing plugins.

        Args:
            plugin: The plugin to add to this Micron object.

        Returns:
            This Micron instance, useful for fluent syntax.
        """
        self.plugins.add(plugin)
        return self

    def configure(self, **configuration):
        """Updates the configuration for this Micron instance.

        Args:
            **configuration: Configuration options that define in what way
                Micron methods that are created using this Micron instance
                must behave. These configuration options can be overridden
                by method-specific configuration options, defined in the
                @micron.method(...) decorator.

        Returns:
            This Micron instance, useful for fluent syntax.

        Example:

            from flask import Flask
            from flask_micron import Micron

            app = Flask(__name__)
            micron = Micron(app).configure(csrf=False)
        """
        self.config.configure(**configuration)
        return self

    def method(self, rule=None, **configuration):
        """Decorates a function to make it work as a Micron method.

        Args:
            rule: The URL rule to use for this method.
                Default: /<name of decorated function>
            **configuration: Configuration options that define in what way
                the Micron method must behave. These configuration options
                can be used to override the default configuration as set
                for the Micron object.

        Returns:
            A decorator that will take care of embedding the Micron method
            in the Flask application and hooking it up with the Micron
            request handling.

        Example:

            from flask import Flask
            from flask_micron import Micron

            app = Flask(__name__)
            micron = Micron(app, csrf=True)

            @micron.method(csrf=False)
            def hello(who="World"):
                return "Hello, %s" % who
        """
        def decorator(func):
            """Wraps a function in a MicronMethod and add it to the URL
            routing of the related Flask app.

            Args:
                func: The function to wrap.
            """
            if self.app is None:
                raise ImplementationError(
                    'The @micron.method decorator can only be used when '
                    'the Micron class is linked to a Flask app')
            micron_method = MicronMethod(self, func).configure(**configuration)
            _add_micron_method_to_flask_app(self.app, micron_method, rule)
            return func
        return decorator


def _add_micron_method_to_flask_app(app, micron_method, rule=None):
    """Adds a URL rule for a Micron method to the Flask app.

    Args:
        app: The Flask app to add the URL rule to.
        micron_method: The Micron method that implements the route.
        rule: The URL rule to use. When no rule is provided, then a rule
            will be automatically derived from the Micron method's name.
    """
    if rule is None:
        rule = _create_url_rule(micron_method)
    app.add_url_rule(rule, view_func=micron_method, methods=['POST'])


def _create_url_rule(micron_method):
    """Creates the URL rule for a Micron method.

    Args:
        micron_method: The MicronMethod to create the route for.

    Returns:
        The URL rule: "/<function name>"
    """
    name = micron_method.__name__.split('.')[-1]
    return '/' + name
