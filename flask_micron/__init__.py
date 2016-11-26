# -*- coding: utf-8 -*-
"""
    flask_micron
    ~~~~~~~~~~~~

    A method-oriented microservice JSON framework on top of the excellent
    Flask package, focusing on security and productivity.

    :copyright: (c) 2016 by Maurice Makaay
    :license: BSD, see LICENSE for more details.
"""

import flask
from flask_micron.micron import Micron
from flask_micron.plugin import Plugin
from flask_micron.errors import MicronError
from flask_micron.errors import MicronServerError
from flask_micron.errors import MicronClientError


__version__ = "0.1.0"
