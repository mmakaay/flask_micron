.. _dev_plugins:

Plugins
=======

Flask-Micron is in its core a plugin system. Plugins can be used
to add extra features to the request handling. The built-in request
handling is fully implemented using plugins as well.

This section explains the plugin system. We will start by explaining
the :ref:`hooks <dev_plugins_hooks>` (extension points) that are available
in Flask-Micron, followed by information about writing actual
:ref:`plugins <dev_plugins_plugin>` and the use of the
:ref:`plugin context <dev_plugins_context>` for passing
data between Flask-Micron and its plugins.

.. _dev_plugins_hooks:

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
| **process_input**      | Post-process the input data (typical use:   |
|                        | data checking and normalization)            |
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

.. _dev_plugins_writeplugin:

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
explained in :ref:`dev_plugins_context`.

**Duck typing**

It is not strictly required to derive from :class:`MicronPlugin
<flask_micron.MicronPlugin>` in order to create a plugin. In the tradition of
Python, Duck Typing is allowed, meaning that you can register any object
as a plugin, as long as it provides the expected plugin hook functions.

In fact, Flask-Micron goes even a step further by accepting objects that
implement only a subset of the plugin hook functions ("Crippled Duck Typing"?)

Example: plugin as a basic object::

    from flask_micron import AccessDenied

    class MyFirstPlugin(object):
    
        def check_access(self, ctx):
            if request.remote_addr != '127.0.0.1':
                raise AccessDenied("Please go home and try again")

Example: plugin as a module::

    from flask_micron import AccessDenied

    def check_access(self, ctx):
        if request.remote_addr != '127.0.0.1':
            raise AccessDenied("Please go home and try again")

.. _dev_plugins_context:

Plugin Context
--------------

Every hook function in a plugin receives the same input: a
:class:`MicronPluginContext
<flask_micron.micron_plugin_context.MicronPluginContext>`. This object
holds the data that is required by plugins for request handling.

At the start of a request, a context object is created by :class:`MicronMethod
<flask_micron.micron_method.MicronMethod>`. The context object properties
``function`` and ``config`` are set. Then, all plugin hook functions
are called with this context object as their input. The hook functions are
responsible for enriching the context data.

When writing a plugin, then keep in mind that the hooks represent a logical
request handling flow. Consequently, for each hook there is a specific    
way in which the context data should be used. In the table below, you can
find the rules for this:                                          

+------------------------+-----------+----------+----------+----------+   
| Hook name              | input     | output   | response | error    |   
+========================+===========+==========+==========+==========+   
| **start_request**      |           |          |          |          |   
+------------------------+-----------+----------+----------+----------+   
| **check_access**       |           |          |          |          |   
+------------------------+-----------+----------+----------+----------+   
| **after_check_access** |           |          |          |          |   
+------------------------+-----------+----------+----------+----------+   
| **read_input**         | WRITE     |          |          |          |   
+------------------------+-----------+----------+----------+----------+   
| **process_input**      | MODIFY    |          |          |          |   
+------------------------+-----------+----------+----------+----------+   
| **call_function**      | READ      | WRITE    |          |          |   
+------------------------+-----------+----------+----------+----------+   
| **process_output**     | READ      | MODIFY   |          |          |   
+------------------------+-----------+----------+----------+----------+   
| **create_response**    | READ      | READ     | WRITE    |          |   
+------------------------+-----------+----------+----------+----------+   
| **process_error**      | READ      | READ     | MODIFY   | READ     |   
+------------------------+-----------+----------+----------+----------+   
| **process_response**   | READ      | READ     | MODIFY   | READ     |   
+------------------------+-----------+----------+----------+----------+   
| **end_request**        | READ      | READ     | READ     | READ     |   
+------------------------+-----------+----------+----------+----------+   
                                                                          
You might have noticed that the ``error`` property is only marked as READ.
The reason for this, is that the Flask-Micron code takes care of setting
that property when an unhandled exception pops up.

                                                            
.. _dev_plugins_usingplugin:

Using your plugin
-----------------

Once you have created a plugin class, you can use it to your Flask-Micron
application by adding it to the :class:`Micron <flask_micron.Micron>` object::

    from flask_micron import Micron
    from flask import Flask
    from your_plugin_module import MyFirstPlugin

    micron = Micron(Flask(__name__)
    micron.plugin(MyFirstPlugin())

In you you created a module-based plugin (let's say in the file
``your_package/plugin_module.py``, you would register it with
Flask-Micron like this::

    from flask_micron import Micron
    from flask import Flask
    from your_package import plugin_module

    micron = Micron(Flask(__name__)
    micron.plugin(plugin_module)
