.. _user_plugins:

Creating plugins
================

Flask-Micron is in its core a plugin system. Plugins can be used
to add extra features to the request handling. The built-in request
handling is fully implemented using plugins as well.

This section explains how to make use of the plugin system to
extend the Flask-Micron functionality.

.. _user_plugins_hooks:

Hooks
-----

Flask-Micron plugins are based on a simple hook pattern. When processing a
request, the :class:`MicronMethod <flask_micron.micron_method.MicronMethod>`
class triggers a set of hooks that represent distinct steps within the
request handling process.

When writing a plugin, you basically write some functions for handling one
or more of these hooks. This makes it possible to let a plugin execute
bits of code at various stages of the request handling process.

During the lifetime of a single request, the following hooks are triggered
(the *[Single]* annotation will be explain below):

+------------------------+---------------------------------------------+
| Hook name              | Intended purpose of the hook                |
+========================+=============================================+
| **request_methods**    | Provide a list of request methods that are  |
|                        | accepted for request handling.              |
+------------------------+---------------------------------------------+
| **start_request**      | Initialize the plugin.                      |
+------------------------+---------------------------------------------+
| **check_access**       | Implement access control (typical use:      |
|                        | authentication, authorization,              |
|                        | blacklisting, rate limiting, etc.)          |
+------------------------+---------------------------------------------+
| **after_check_access** | Perform tasks that are not fully related    |
|                        | to the actual request, but that must be     |
|                        | performed after the check_access hook       |
|                        | (typical use: auth session keep-alive)      |
+------------------------+---------------------------------------------+
| **read_input**         | Read request data from Flask's ``request``  |
|                        | and turn it into a Python datastructure     |
|                        | (called 'input data'). This is where the    |
|                        | default Flask-Micron plugin deserializes    |
| *[Single]*             | the JSON payload from a POST request.       |
+------------------------+---------------------------------------------+
| **normalize_input**    | Post-process the input data.                |
+------------------------+---------------------------------------------+
| **validate_input**     | Check for valid input data.                 |
+------------------------+---------------------------------------------+
| **call_function**      | Call the function that is wrapped as a      |
|                        | Micron method, feeding it the input data,   |
|                        | and capturing the return value from that    |
| *[Single]*             | function (called 'output data')             |
+------------------------+---------------------------------------------+
| **process_output**     | Post-process the output data (typical use:  |
|                        | data checking and normalization)            |
+------------------------+---------------------------------------------+
| **create_response**    | Create a Flask ``Response`` object, based   |
|                        | on the output data. This is where the       |
|                        | default Flask-Micron plugin serializes the  |
|                        | output data into JSON and creates a         |
| *[Single]*             | response of content type application/json.  |
+------------------------+---------------------------------------------+
| **process_error**      | Act on exceptions that are raised during    |
|                        | request handling (typical use: logging)     |
|                        | This hook is of course only triggered when  |
|                        | an actual Exception is raised.              |
+------------------------+---------------------------------------------+
| **process_response**   | Post-process the Flask ``Response`` object. |
+------------------------+---------------------------------------------+
| **end_request**        | Teardown the plugin.                        |
+------------------------+---------------------------------------------+

A few hooks are annotated with *[Single]* in the table. These hooks are
somewhat special. For most of the hooks, Flask-Micron will call the
corresponding hook function in every registered plugin. For the *[Single]*
hooks however, only the hook function from the plugin that was registered
last is called. 

The reason for this, is that for those steps in the request processing, it
makes no sense to perform them multiple times. The request can only be read
once, the function must be called only once and the response can only be
created once.

Put differently: when implementing a *[Single]* hook function, your plugin
will override existing behavior. Other hook functions will extend the behavior.

.. _user_plugins_writeplugin:

How to write a plugin
---------------------

A Flask-Micron plugin is nothing more than a collection of hook functions.
Hook functions have the same name as the hook that they must act upon.

The standard way to implement a plugin, is to derive a class from the
:class:`MicronPlugin <flask_micron.MicronPlugin>` class. The derived plugin
class can override methods to implement the hooks that it needs for its
functionality.

Example: plugin as a derived MicronPlugin class::

    from flask_micron import MicronPlugin
    from flask_micron.errors import AccessDenied

    class MyFirstPlugin(MicronPlugin):
    
        def check_access(self, ctx):
            if request.remote_addr != '127.0.0.1':
                raise AccessDenied("Please go home and try again")

You might be wondering: "What is that ``ctx`` argument?" This will be
explained in :ref:`user_plugins_context`.

**Duck typing**

It is not strictly required to derive from :class:`MicronPlugin
<flask_micron.MicronPlugin>` in order to create a plugin. In the tradition of
Python, Duck Typing is allowed, meaning that you can register any object
as a plugin, as long as it provides the expected plugin hook functions.

In fact, Flask-Micron goes even a step further by accepting objects that
implement only a subset of the plugin hook functions ("Crippled Duck Typing"?)

Example: plugin as a basic object::

    from flask_micron.errors import AccessDenied

    class MyFirstPlugin(object):
    
        def check_access(self, ctx):
            if request.remote_addr != '127.0.0.1':
                raise AccessDenied("Please go home and try again")

Example: plugin as a module::

    from flask_micron.errors import AccessDenied

    def check_access(ctx):
        if request.remote_addr != '127.0.0.1':
            raise AccessDenied("Please go home and try again")

.. _user_plugins_context:

Plugin Context
--------------

Every hook function in a plugin is called with the same argument: a
:class:`MicronPluginContext
<flask_micron.micron_plugin_context.MicronPluginContext>` object. This object
holds the data that are required by plugins for request handling. The following
properties are availble in the context:

* **function**: The function that is wrapped by the MicronMethod.
* **config**: The configuration for the MicronMethod, flattened as a dict 
  (see :ref:`user_plugins_configurable`)
* **input**: The input data for the function (the Flask ``request`` translated
  into a Python data structure).
* **output**: The return value of the function.
* **response**: The Flask ``Response`` object to return to the caller.
* **error**: The exception object, in case an unhandled exception is raised
  from a plugin.

At the start of a request, a context object is created by the
:class:`MicronMethod <flask_micron.micron_method.MicronMethod>`. Then, all
plugin hook functions are called with this context object as their input. The
hook functions are responsible for enriching the context data.

The hooks represent a logical request handling flow. Consequently, for each
hook there is a specific way in which the context data should be used. In the
table below, you can find the data access rules for all context properties.

+--------------------+----------+--------+--------+--------+----------+-------+
| Hook name          | function | config | input  | output | response | error |
+====================+==========+========+========+========+==========+=======+
| request_methods    | READ     | MODIFY |        |        |          |       |
+--------------------+----------+--------+--------+--------+----------+-------+
| start_request      | READ     | MODIFY |        |        |          |       |
+--------------------+----------+--------+--------+--------+----------+-------+
| check_access       | READ     | READ   |        |        |          |       |
+--------------------+----------+--------+--------+--------+----------+-------+
| after_check_access | READ     | READ   |        |        |          |       |
+--------------------+----------+--------+--------+--------+----------+-------+
| read_input         | READ     | READ   | WRITE  |        |          |       |
+--------------------+----------+--------+--------+--------+----------+-------+
| normalize_input    | READ     | READ   | MODIFY |        |          |       |
+--------------------+----------+--------+--------+--------+----------+-------+
| validate_input     | READ     | READ   | READ   |        |          |       |
+--------------------+----------+--------+--------+--------+----------+-------+
| call_function      | READ     | READ   | READ   | WRITE  |          |       |
+--------------------+----------+--------+--------+--------+----------+-------+
| process_output     | READ     | READ   | READ   | MODIFY |          |       |
+--------------------+----------+--------+--------+--------+----------+-------+
| create_response    | READ     | READ   | READ   | READ   | WRITE    |       |
+--------------------+----------+--------+--------+--------+----------+-------+
| process_error      | READ     | READ   | READ   | READ   | MODIFY   | READ  |
+--------------------+----------+--------+--------+--------+----------+-------+
| process_response   | READ     | READ   | READ   | READ   | MODIFY   | READ  |
+--------------------+----------+--------+--------+--------+----------+-------+
| end_request        | READ     | READ   | READ   | READ   | READ     | READ  |
+--------------------+----------+--------+--------+--------+----------+-------+
 
* **WRITE**: The hook must store new data
* **MODIFY**: The hook can read the data and can modify or replace it
* **READ**: The hook can read the data

You might have noticed that no WRITE option is defined for the properties
**function**, **config** and **error**. The reason for this, is that the 
Flask-Micron core code is responsible for setting these.

Another thing you might have noticed, is that all hooks that have the WRITE
option correspond to the hooks that were annotated with *[Single]* in the
:ref:`user_plugins_hooks` section. This is no coincidence, since these hooks
are responsible for setting the initial value of the related properties.

When you play by above rules, you are being a good citizen (kudos for that)
and you can rest assured that your plugin won't run into conflicts with
other plugins.

.. _user_plugins_usingplugin:

Using your plugin
-----------------

Once you have created a plugin class, you can use it with your Flask-Micron
application by adding it to the :class:`Micron <flask_micron.Micron>` object::

    from flask import Flask
    from flask_micron import Micron
    from your_plugin_module import MyFirstPlugin

    micron = Micron(Flask(__name__)
    micron.plugin(MyFirstPlugin())

In you you created a module-based plugin (let's say in the file
``your_package/plugin_module.py``, you would register it with
Flask-Micron like this::

    from flask import Flask
    from flask_micron import Micron
    from your_package import plugin_module

    micron = Micron(Flask(__name__)
    micron.plugin(plugin_module)

.. _user_plugins_configurable:

Making plugin behavior configurable
-----------------------------------

When your plugin can display different kinds of behavior, and you need
to be able to differentiate this behavior per Micron method, then you can
make use of the Micron configuration handling.

Configuration can be done at two levels:

1. The Micron object
2. The @micron.method() decorator

Configuration at the level of the Micron object is used for all functions
that are decorated using that object. The ``@micron.method()`` decorator
configuration can be used to override the configuration per decorated
function. Here's an example::

    app = Flask(__name__)
    micron = Micron(app, configA='plug', configB='in')

    @micron.method(configA='drive')
    def hello():
        return "Hello, world!"

    @micron.method(configC='peep')
    def bye():
        return "Bye, world!"

When Micron processes a request, it will flatten the configuration options
from Micron and the @micron.method decorator into a single dict and pass it to
plugin hook functions via the context object. For the above example, you would
see the following configuration data in the plugin context::

    hello()     ctx.config = {
                    "configA": "drive",
                    "configB": "in"
                }

    bye()       ctx.config = {
                    "configA": "plug",
                    "configB": "in",
                    "configC": "peep"
                }

Here's an example of how you could access these configuration options from
within a hook function, and fall back to a default value when a configuration
option is not defined in either Micron or the @micron.method decorator::

	def normalize_input(self, ctx):
		ctx.input.things = [
			ctx.config.get('configA', 'defaultA'),
			ctx.config.get('configB', 'defaultB'),
			ctx.config.get('configC', 'defaultC')
		]

Another way to work with default values, could be to resolve the default
values in the ``start_request`` hook function, so other hook functions can
be assured that all configuration values are set::

	def start_request(self, ctx):
		ctx.config.setdefault('configA', 'defaultA')
		ctx.config.setdefault('configB', 'defaultB')
		ctx.config.setdefault('configC', 'defaultC')

	def normalize_input(self, ctx):
		ctx.input.things = [
			ctx.config['configA'],
			ctx.config['configB'],
			ctx.config['configC']
		]

Beware that the configuration space is shared by all plugins. Therefore
use configuration names that are not likely to collide with other plugins.

.. _user_plugins_globalconfiguration:

Global plugin configuration
---------------------------

When your plugin requires some global configuration, for example the
connection details for a database connection, then don't implement this
using the configuration system as described above. That system is primarily
designed for configuration options that might differ per method.

Example of a clean implementation::

    flask = new Flask(__name__)
    micron = Micron(flask)
    my_plugin = MyPlugin("my_plugin.conf")
    micron.plugin(plugin)

    @micron.method(my_option=42)
    def give_me_one():
        return 1

In this example, the fictional MyPlugin loads its global configuration from
the file ``my_plugin.conf``, while the ``my_option`` parameter is used for
tweaking the plugin behavior at the Micron method level.

This style is highly preferred above a style where global configuration data
is put in the Micron method configuration::

    flask = new Flask(__name__)
    micron = Micron(flask,
        my_plugin_dbhost="127.0.0.1",
        my_plugin_dbuser="myuser",
        my_plugin_dbpass="mypass")
    my_plugin = MyPlugin()
    micron.plugin(my_plugin)

    @micron.method(my_option=42)
    def give_me_one():
        return 1

This style of coding would technically work, but it mixes global
configuration with Micron method configuration. One of the biggest
problems that I see with this style, is that environment configuration
is highly coupled with the code. Moving code between environments
becomes hard this way.

This might be a good cue for pointing you at "The 12-Factor App".
This is a resource that should be read by *"Any developer building
applications which run as a service."* That's you! In regards to
this section, the section on configuration management is especially
interesting:

https://12factor.net/config

Sharing data between hook functions
-----------------------------------

To share request data from one hook function to another, beware not to
use global variables or properties on your plugin object. This would
break in the most horrible ways in threaded environments! 

Instead, you can make use of ``flask.g``, a standard Flask construct
for storing data for a single request, fully prepared for multi-threading.
For information on this, take a look at the Flask documentation:

http://flask.pocoo.org/docs/api/#application-globals

Here's an example of how you would use ``flask.g`` in your plugin::

    from flask import g, request
    from flask_micron import MicronPlugin
    from timeit import default_timer as timer
    
    class RequestTimer(MicronPlugin):

        def start_request(self, ctx):
            g.start_time = timer() 

        def process_response(self, ctx):
            end_time = timer()
            diff = round((end_time - g.start_time) * 1000, 2)
            diff_str = "%s ms" % diff
            ctx.response.headers['X-Micron-RequestTimer'] = diff_str

This plugin records the start time for the request in ``flask.g.start_time``.
By the time that a response has been cooked up, the plugin uses the recorded
start time to determine how long request processing took. This time is
then added to the response headers. Below, (part of) the response headers
for a request that uses the above plugin:: 

    HTTP/1.0 200 OK
    Content-Type: application/json
    X-Micron-CSRF-Token: 90dfd8d6-31e6-47f2-a153-ea68b866a6a5
    X-Micron-RequestTimer: 1.36 ms
    Server: Werkzeug/0.11.11 Python/3.5.2

Self-Shunt: Quick 'n Dirty Pluggin'
-----------------------------------

Let's say that you are writing a simple single file web service using
Flask-Micron and feel the need for some plugin features, without feeling
the love for having to create a full fledged plugin. In this case, you
might like the following pattern::

    from flask import Flask
    from flask_micron import Micron
    from time import time

    def process_response(ctx):
       ctx.response.headers['X-Micron-I-Was'] = "here!" 

    micron = Micron(Flask(__name__).plugin(globals())

    @micron.method()
    def get_epoch():
        return round(time())

Note that it is important that ``plugin(globals())`` is called *after*
defining the required hook function(s).
        
.. note::
    I call the pattern "Self-Shunt", because of its similarities with the
    unit testing Self-Shunt pattern. In unit testing it means that you
    write a test class, which injects itself as a dependency in the
    tested code.
