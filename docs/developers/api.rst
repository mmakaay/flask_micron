.. _api:

Public API
==========

This section contains the low-level API documentation for Flask-Micron.

Micron
------

.. currentmodule:: flask_micron
.. autoclass:: Micron
    :members:

flask_micron.Plugin
-------------------

.. currentmodule:: flask_micron
.. autoclass:: Plugin
    :members:

flask_micron.plugin.Context
---------------------------

.. currentmodule:: flask_micron.plugin
.. autoclass:: Context
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

.. currentmodule:: flask_micron.method
.. autoclass:: MicronMethod
    :members:

MicronMethodConfig
------------------

.. currentmodule:: flask_micron.method
.. autoclass:: MicronMethodConfig
    :members:

flask_micron.plugin.Container
-----------------------------

.. currentmodule:: flask_micron.plugin
.. autoclass:: Container
    :members:
