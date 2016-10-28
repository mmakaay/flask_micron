"""This module implements an plugin for Flask-Micron to use JSON data as
input for Micron methods."""

from flask import json
from flask import request
from flask_micron.errors import MicronClientError
from flask_micron.micron_plugin import MicronPlugin


class NonJsonInput(MicronClientError):
    """The POST body for the request did not contain valid JSON data."""


class Plugin(MicronPlugin):
    """A plugin to retrieve the input data for the Micron method from
    the request.

    The request data must either be absent or a valid JSON string in
    the request POST body.
    """

    def read_input(self, ctx):
        """Reads the input data and stores it in the MicronPluginContext."""
        ctx.input = None
        post_body = request.data

        if post_body is None:
            return

        # Added to make the flask app.test_client() work with Micron.
        # When using the test client, the post body contains a bytes object.
        if isinstance(post_body, bytes):
            post_body = post_body.decode('utf-8')

        if isinstance(post_body, str) and post_body.strip() == "":
            return

        try:
            ctx.input = json.loads(post_body)
        except Exception:
            raise NonJsonInput()
