"""This module contains configuration for the Micron package."""

# TODO still needed or replace with neat context wrapper?

import flask


SESSION_INTERFACE = flask.session
"""The object to use as the session store for the whole of Micron.
By default the Flask session object is used, but it can be overridden
(for testing purposes).

When replacing this interface with another one, then a basic dict interface
will do. Micron treats the session data as a dict an only sets and gets
data by key.
"""

REQUEST_INTERFACE = flask.request
"""The object to use as the request for the whole of Micron.
By default the Flask request object is used, but it can be overridden,
e.g. for testing purposes.

When replacing this interface with another one, then provide an object
that contains at least the following properties:
    data: the POST body data to work with
    headers: a dict of request headers
"""
