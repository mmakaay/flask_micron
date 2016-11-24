.. _api:

Public API
==========

This section contains the low-level API documentation for Flask-Micron.

Micron
------

.. currentmodule:: flask_micron
.. autoclass:: Micron
    :members:

MicronPlugin
------------

.. currentmodule:: flask_micron
.. autoclass:: MicronPlugin
    :members:

MicronPluginContext
-------------------

.. currentmodule:: flask_micron.micron_plugin_context
.. autoclass:: MicronPluginContext
    :members:

Errors
------

Base type for all Flask-Micron exceptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: flask_micron
.. autoclass:: MicronError
    :show-inheritance:

Derive from these to create your own exceptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: MicronServerError
    :show-inheritance:

.. autoclass:: MicronClientError
    :show-inheritance:

Exceptions ready for use in your own code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: flask_micron.errors

.. autoclass:: AccessDenied
    :show-inheritance:

.. autoclass:: AuthenticationRequired
    :show-inheritance:

.. autoclass:: AuthenticationFailed
    :show-inheritance:

.. autoclass:: AuthorizationFailed
    :show-inheritance:

.. autoclass:: ImplementationError
    :show-inheritance:

.. autoclass:: UnhandledException
    :show-inheritance:

.. _api_internal:

Internal Components
===================

MicronMethod
------------

.. currentmodule:: flask_micron.micron_method
.. autoclass:: MicronMethod
    :members:

MicronMethodConfig
------------------

.. currentmodule:: flask_micron.micron_method_config
.. autoclass:: MicronMethodConfig
    :members:

MicronPluginContainer
---------------------

.. currentmodule:: flask_micron.micron_plugin_container
.. autoclass:: MicronPluginContainer
    :members:
