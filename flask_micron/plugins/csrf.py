"""This module implements a CSRF protection plugin for Flask-Micron.

What is CSRF?

    CSRF = Cross-Site Request Forgery

    This is a type of attack where a user is logged into site A, then visits
    site B which tells the browser "Do this bad thing on site A".
    Without CSRF protection, site A actually performs the "bad thing".

    For more in depth info on CSRF, take a look at:
    https://www.owasp.org/index.php/Cross-Site_Request_Forgery_(CSRF)


Mode of operation:

    On every request, this module will generate a fresh CSRF protection
    token. This token is stored in the Flask session and it is communicated
    to the client using an X-Micron-CSRF-Token HTTP response header.

    In the next request, the client must send this token back in an
    X-Micron-CSRF-Token HTTP request header. When CSRF checking is enabled
    for the requested method (which is the default) and the client does not
    send this header or the value for the header is not a valid token (i.e.
    it is not known in the session), the request will be rejected.

    To bootstrap this operation, an initial call is required for which CSRF
    checking is not enabled. For this purpose, Micron offers the method
    'ping' by default. Of course, it is also possible to provide your own
    unprotected method for bootstrapping. Just make sure that unprotected
    methods perform no important operations.


At the HTTP level:

    Let's send a request to the "Hello, world" method that you can find
    in the example code from below:

        POST /hello HTTP/1.1
        Host: localhost
        Content-Length: 8

        "Micron"

    The method is CSRF protected, however we did not provide a CSRF token.
    For that reason, the request is rejected:

        HTTP/1.0 500 SERVER ERROR
        Content-Type: application/json
        X-Micron-CSRF-Token: 24ce3eac-5307-4cff-bcb8-ff0d5945f685

        {
          "caused_by": "client",
          "code": "CsrfTokenRequired",
          ...
        }

    In the example response from above, you can see that errors messages
    will also provide a CSRF token. A client could of course use that token
    and resubmit the request, but for bootstrapping it is cleaner to start
    out with a method like ping:

        POST /ping HTTP/1.1
        Host: localhost

    In the server response, a token is provided:

        HTTP/1.0 200 OK
        X-Micron-CSRF-Token: a85892c2-ec35-42ef-9516-3b33eabe853b

        "pong"

    Now we can send a request to "Hello, world" using this token:

        POST /hello HTTP/1.1
        Host: localhost
        Content-Length: 8
        X-Micron-CSRF-Token: a85892c2-ec35-42ef-9516-3b33eabe853b

        "Micron"

    Since a valid CSRF token is provided, the server now responds:

        HTTP/1.0 200 OK
        X-Micron-CSRF-Token: 7b81b93a-e52a-4941-8cf8-d846a97d0dec

        "Hello, Micron!"

    And as you can see, along with the method result, the following
    CSRF token is provided.


Usage:

    This is a core plugin, automatically loaded by Micron.
    Therefore you can use it right away, without having to load it:

        from flask import Flask
        from flask_micron import Micron

        app = Flask(__name__)
        micron = Micron(app)

        @micron.method(csrf=True)
        def hello(who="World"):
            return 'Hello, %s!' % who

        @micron.method(csrf=False)
        def not_protected():
            return 'I am not CSRF protected'

    The CSRF checking option is automatically enabled. Therefore, you could
    omit the configuration option csrf=True. If you want to disable CSRF
    checking for a complete Micron instance, then you can do:

        app = Flask(__name__)
        micron = Micron(app).configure(csrf=False)
"""

import uuid
from flask import request
from flask import session
from flask_micron.errors import MicronClientError
from flask_micron.micron_plugin import MicronPlugin


MAX_NUMBER_OF_CSRF_TOKENS_TO_STORE = 3
"""The number of tokens to keep around in the session data.
By remembering a few recent tokens, we prevent issues with concurrent
calls from an asynchroneously operating UI.

Two example issue scenarios:

- Issue: multiple calls using the same CSRF token

  client sends request 0
  gets response 0 with new token 'A'
  sends request 1 with token 'A' <- using token
  sends request 2 with token 'A' <- reusing the same token
  gets response 1 with new token 'B'
  gets response 2 with new token 'C'

- Issue: different tokens being processed in the wrong order

  client send request 0
  gets response 0 with new token 'A'
  sends request 1 with token 'A'
  sends request 2 with token 'A'
  gets response 1 with new token 'B'
  sends request 3 with token 'B'
  gets response 2 with new token 'C'
  sends request 4 with token 'C'
  server processes request 4 with token 'C' <- this request might be processed
  server processes request 3 with token 'B' <- before this one
  got response 4 with new token 'D'
  got response 3 with new token 'E'

  Both problems are circumvented by remembering a recent set of
  CSRF tokens instead of only one.

  Another way of solving these issues, would be to generate a single CSRF
  token per user session and use that one for all calls, but to me that
  seems like an easy way out.
"""

CSRF_TOKEN_HEADER = 'X-Micron-CSRF-Token'
"""The name of the header that is used for transporting CSRF tokens between
the client and the server (so it used both by the server to provide a
fresh CSRF token to the client and the by the client to provide a CSRF token
for a request).
"""

SESSION_KEY = 'fm_CT'
"""The key that is used to store valid csrf tokens in the session.

It has no special meaning, but it is only used as a non-obvious key
to prevent conflicts with other users of the session object.
"""


class CsrfTokenRequired(MicronClientError):
    """A method was called for which CSRF checking is enabled, but
    the client did not provide a CSRF token in the request.
    """


class CsrfTokenInvalid(MicronClientError):
    """A method was called for which CSRF checking is enabled, but
    the client provided a CSRF token in the request that is
    not valid (anymore).
    """


class Plugin(MicronPlugin):
    """A CSRF protection plugin for Micron."""

    def check_access(self, ctx):
        """Checks for an CSRF token in the CSRF token request header and
        checks if its value is a valid CSRF token.
        """
        if ctx.config.get('csrf', True):
            headers = request.headers
            provided_token = _extract_token_from_headers(headers)
            if provided_token is None:
                raise CsrfTokenRequired()
            if provided_token not in _get_tokens():
                raise CsrfTokenInvalid()

    def process_response(self, ctx):
        """Generates a new CSRF token, adds it to the session data and
        hands over the token to the client through the CSRF token
        header in the response.
        """
        new_token = _generate_token()
        _store_token(new_token)
        ctx.response.headers[CSRF_TOKEN_HEADER] = new_token


def _extract_token_from_headers(headers):
    """Retrieves the value of the CSRF token header from the request
    headers. According to the HTTP specification, the lookup is done in
    a case-insensitive way.
    """
    header_name = str.lower(CSRF_TOKEN_HEADER)
    for key in headers.keys():
        if str.lower(key) == header_name:
            return headers[key]
    return None


def _generate_token():
    """Generates a new random CSRF token.

    :returns:
        A random CSRF token.
    """
    return str(uuid.uuid4())


def _store_token(token):
    """Stores a CSRF token in the session data.

    We keep a few CSRF tokens around, which will handle cases where
    multiple requests fire simultaneously in the browser, possibly
    causing use of an already used CSRF token or out-of-order use
    of generated CSRF tokens.
    """
    tokens = _get_tokens()
    tokens.append(token)
    while len(tokens) > MAX_NUMBER_OF_CSRF_TOKENS_TO_STORE:
        tokens.pop(0)

    session[SESSION_KEY] = tokens


def _get_tokens():
    return session.get(SESSION_KEY, [])
