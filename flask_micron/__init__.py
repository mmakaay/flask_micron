"""
    flask_micron
    ~~~~~~~~~~~~

    A method-oriented microservice JSON framework on top of the excellent
    Flask package, focusing on security and productivity.

    :copyright: (c) 2016 by Stichting FiberOveral
    :license: BSD, see LICENSE for more details.
"""

import flask
from flask_micron.micron import Micron
from flask_micron.errors import MicronClientError
from flask_micron.errors import MicronServerError
from flask_micron.micron_plugin import MicronPlugin


__version__ = "0.0.1"
