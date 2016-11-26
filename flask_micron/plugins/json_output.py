# -*- coding: utf-8 -*-
#pylint: disable=too-many-return-statements

"""This plugin produces a JSON response for a request.

Mode of operation
-----------------

The plugin takes the ``ctx.output`` data. This is the data that was returned
by the wrapped function. This data is serialized into JSON.

The JSON data is put in a `Flask`_ ``Response`` object, which is stored
in ``ctx.response``.

Members
-------
"""

from datetime import datetime
from datetime import timedelta
from flask import json
from flask.wrappers import Response
from flask_micron.errors import ImplementationError
from flask_micron import plugin


class Plugin(plugin.Plugin):
    """A plugin to create the response for a Micron method as a
    JSON-serialized message.
    """
    def create_response(self, ctx):
        """Serialize the Micron method output as JSON data and create the
        Flask Response object.
        """
        ctx.response = Response(
            json.dumps(ctx.output, indent=2, default=_serializer_hook),
            status=200 if ctx.error is None else 500,
            content_type="application/json"
        )


def _serializer_hook(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, timedelta):
        return str(value)
    if isinstance(value, bytes):
        return value.decode('utf-8')
    if isinstance(value, str):
        return value
    raise ImplementationError(
        "Unsupported type '%s' used in response data "
        "(no support for JSON serializing this type)" % type(value).__name__)
