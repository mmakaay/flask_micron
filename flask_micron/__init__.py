# -*- coding: utf-8 -*-
"""
flask_micron
============

The ``flask_micron`` module exposes some of the important Flask-Micron
classes as members of this module, so you can import them from one
conventient place:

* :any:`Micron`
* :any:`MicronPlugin`
* :any:`MicronError`
* :any:`MicronServerError`
* :any:`MicronClientError`

So for example, instead of::

    from flask_micron.micron import Micron

you can make use of::

    from flask_micron import Micron


:copyright: (c) 2016 by Maurice Makaay
:license: BSD, see :ref:`license` for more details.
"""

import flask
from flask_micron.micron import Micron
from flask_micron.plugin import Plugin
from flask_micron.errors import MicronError
from flask_micron.errors import MicronServerError
from flask_micron.errors import MicronClientError


__version__ = "0.1.0"
