# -*- coding: utf-8 -*-
"""This plugin lets Flask-Micron accept JSON input on a POST request.

Mode of operation
-----------------

The POST body is read from the incoming `Flask`_ request.

* When this body contains a valid JSON string, it is deserialized and
  stored in ``ctx.input``.
* When no data is provided in the body (strictly speaking, not a valid JSON
  input string), then ``ctx.input`` is set to ``None``.
* When invalid data is provided, a ``NonJsonInput`` exception is raised.

Note: ``ctx`` refers to a :ref:`plugin context <user_plugins_context>`.

Members
-------
"""

from flask import json
from flask import request
from flask_micron.errors import MicronClientError
from flask_micron import plugin
from flask_micron.compat import is_string


class Plugin(plugin.Plugin):
    """A plugin to read the input for the Micron method from the request."""

    def read_input(self, ctx):
        """Reads the input data and stores it in the plugin context."""
        ctx.input = None
        post_body = request.get_data()

        if post_body is None:
            return

        if isinstance(post_body, bytes):
            post_body = post_body.decode('utf-8')

        if is_string(post_body) and post_body.strip() == "":
            return

        try:
            ctx.input = json.loads(post_body)
        except Exception:
            raise NonJsonInput()


class NonJsonInput(MicronClientError):
    """The POST body for the request did not contain valid JSON data."""
