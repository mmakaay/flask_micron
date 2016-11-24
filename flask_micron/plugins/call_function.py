# -*- coding: utf-8 -*-
"""This plugin calls the function that is wrapped as a Micron method,
using ``ctx.input`` as its argument. The return value is stored in
``ctx.output``.

Mode of operation
-----------------

This plugin takes a very simple and straight-forward approach to call
the wrapped function. The function must take either no or a single
argument, where the single argument version can also define default value.
Below are the possible scenarios.

**The function takes no arguments**

.. code:: python

    @micron.method()
    def the_function():
          ...

| The ``ctx.input`` must be ``None`` in this case.
| The function will be called without arguments:

.. code:: python

     the_function()

**The function takes a single argument**

.. code:: python

    @micron.method()
    def the_function(arg):
        ...

| The ``ctx.input`` must contain a value that is not ``None``.
| The function is called with ``ctx.input`` as the argument:

.. code:: python

     the_function(ctx.input)

**The function takes a single argument, which has a default value**

.. code:: python

    @micron.method()
    def the_function(arg=defaultvalue):
        ...

| The ``ctx.input`` can contain either a value or None.
| The function is called without argument when ``ctx.input`` is ``None``,
| The function is called with ``ctx.input`` as the argument otherwise:

.. code:: python

     if ctx.input is None:
         the_function()
     else
         the_function(ctx.input)

For other scenarios, appropriate exceptions will be raised.

Members
-------
"""

import inspect
from flask_micron.errors import MicronClientError
from flask_micron.errors import ImplementationError
from flask_micron.micron_plugin import MicronPlugin


class Plugin(MicronPlugin):
    """This plugin calls the function that is wrapped as a Micron method,
    using the input data as prepared in the context.
    """
    def call_function(self, ctx):
        signature = _check_function_signature(ctx.function)
        _check_input(signature, ctx.input)
        output = _call_function(ctx.function, signature, ctx.input)
        ctx.output = output


def _check_function_signature(function):
    """Checks the signature of the Micron method. This method must
    take no or exactly one argument, possibly defined with a default
    value for it.

    :param function function:
        the function for which to check the signature

    :returns:
        A tuple containing two elements:
        1. bool: Whether or not the function expects input
        2. bool: Whether or not a default value is defined
    """
    (args, varargs, kwargs, defaults) = _inspect_signature(function)
    if len(args) > 1:
        raise ImplementationError(
            "A Micron method must take either no arguments " +
            "or exactly one argument (so not multiple arguments)")
    if varargs is not None:
        raise ImplementationError(
            "A Micron method must take either no arguments " +
            "or exactly one argument (so no varargs *%s)" % varargs)
    if kwargs is not None:
        raise ImplementationError(
            "A Micron method must take either no arguments " +
            "or a single argument (so no keyword args **%s)" % kwargs)
    return (
        len(args) > 0,
        defaults is not None and len(defaults) > 0
    )


def _inspect_signature(function):
    """Retrieve the signature for the function.
    This function fixes a compatibility issue with Python 3.6+, for which
    inspect.getargspec no longer exists.

    :param function function:
        The function for which to inspect the signature.

    :returns:
        A function signature as returned by inspect.getargspec()
    """
    if hasattr(inspect, 'signature'):
        signature = inspect.signature(function)
        params = signature.parameters.values()
        return (
            [p.name for p in params if p.kind == p.POSITIONAL_OR_KEYWORD],
            next((p.name for p in params if p.kind == p.VAR_POSITIONAL), None),
            next((p.name for p in params if p.kind == p.VAR_KEYWORD), None),
            [p.default for p in params
             if p.kind == p.POSITIONAL_OR_KEYWORD and p.default != p.empty]
        )
    else:
        return inspect.getargspec(function)


def _check_input(signature, data):
    (wants_input, has_default) = signature
    if wants_input and data is None and not has_default:
        raise MissingInput()
    if not wants_input and data is not None:
        raise UnexpectedInput()


def _call_function(function, signature, data):
    (wants_input, _) = signature
    if not wants_input or data is None:
        return function()
    else:
        return function(data)


class MissingInput(MicronClientError):
    """The requested method requires input, but no input was
    provided by the client."""


class UnexpectedInput(MicronClientError):
    """The requested method does not require any input, but input
    was provided by the client."""
