.. _api:

Public API
==========

This section contains the low-level API documentation for Flask-Micron.

Micron
------

.. module:: flask_micron
.. autoclass:: Micron
    :members:

MicronPlugin
------------

.. module:: flask_micron.micron_plugin
.. autoclass:: MicronPlugin
    :members:

MicronPluginContext
-------------------

.. module:: flask_micron.micron_plugin_context
.. autoclass:: MicronPluginContext
    :members:

Errors
------

.. module:: flask_micron.errors
.. autoclass:: MicronError
.. autoclass:: MicronServerError
.. autoclass:: MicronClientError
    :members:

Internal Components
===================

MicronMethod
------------

.. module:: flask_micron.micron_method
.. autoclass:: MicronMethod
    :members:

MicronMethodConfig
------------------

.. module:: flask_micron.micron_method_config
.. autoclass:: MicronMethodConfig
    :members:

MicronPluginContainer
---------------------

.. module:: flask_micron.micron_plugin_container
.. autoclass:: MicronPluginContainer
    :members:

MicronPluginCompiler
--------------------

.. module:: flask_micron.micron_plugin_compiler
.. autoclass:: MicronPluginCompiler
    :members:

Bundled Plugins
===============

CSRF Protection Plugin
----------------------

.. module:: flask_micron.plugins.csrf
.. autoclass:: Plugin
    :members:
