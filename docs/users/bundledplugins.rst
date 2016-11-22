.. _user_bundledplugins:

Bundled plugins
===============

Flask-Micron is in its core a plugin system. Plugins can be used
to add extra features to the request handling. The built-in request
handling is fully implemented using plugins as well.

This section describes the plugins that come bundled with Flask-Micron
and that are loaded by default to make up the standard request handling.

.. _user_bundledplugins-json-input:

Read JSON Input
---------------

| Defined in: ``plugins/json_input.py``
| Hooks into: ``read_input``

This plugin reads the POST body from a request. When the body contains
a valid JSON string, it is deserialized and stored in ``ctx.input``.
When no data is provided in the body, then ``ctx.input`` is set to ``None``.

When invalid data is provided, a ``NonJsonInput`` exception is raised. 

.. _user_bundledplugins-normalize-input:

Normalize Input
---------------

| Defined in: ``plugins/normalize_input.py``
| Hooks into: ``normalize_input``

This plugin normalizes the request data that is stored in ``ctx.input``. 
Normalization is applied recursively to data structures.

Normalization consists of::

* Stripping whitespace from string values
* Making empty strings None

Configuration options:

**normalize**: True/False (default = True)
  Whether or not to apply normalization to the request.

**strip_strings**: True/False (default = True)
  Whether or not to strip leading and trailing whitespace from strings.

**make_empty_strings_none**: True/False (default = True)
  Whether or not empty strings must be normalized to None.

Example::

    @micron.method(
        normalize=True,
        strip_strings=False,
        make_empty_strings_none=True)
    def my_method(arg):
        ...
        ...

.. _user_bundledplugins-call-function:

Call Function
-------------

| Defined in: ``plugins/call_function.py``
| Hooks into: ``call_function``

This plugin calls the function that is wrapped as a Micron method, using
``ctx.input`` as its argument. The return value is stored in ``ctx.output``.

.. _user_bundledplugins-json-output:

JSON Output
-----------

| Defined in: ``plugins/json_output.py``
| Hooks into: ``create_response``

This plugin takes the data from ``ctx.output``, serializes it into JSON
data and creates a `Flask`_ ``Response`` object containing the JSON data.

.. _user_bundledplugins-csrf:

CSRF Protection
---------------

| Defined in: ``plugins/csrf.py``
| Hooks into: ``check_access``, ``process_response``

This module implements CSRF protection for Flask-Micron.
See: :ref:`user_csrf-protection`

Configuration options:

**csrf**: True/False (default = True)
  Whether or not to enable CSRF protection.

