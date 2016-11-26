# -*- coding: utf-8 -*-
# pylint: disable=too-many-branches

"""This plugin adds input data normalization to Flask-Micron.

Mode of operation
-----------------

The plugin takes the datastructure from ``ctx.input`` and normalizes it,
according to the following rules:

* Leading and trailing whitespace are stripped from string values.
* Strings that are empty are set to ``None``.

Normalization is applied to:

* strings
* dicts (recursively)
* lists (recursively)

Configuration options
---------------------

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

Members
-------
"""
from flask_micron import plugin
from flask_micron.compat import is_string


class Plugin(plugin.Plugin):
    """An input normalization plugin for Micron.  """

    def normalize_input(self, ctx):
        """Normalizes input data.

        :param ctx:
            The plugin context, containing the data to normalize.
        """
        if ctx.config.get('normalize', True):
            strip_strings = ctx.config.get('strip_strings', True)
            make_empty_none = ctx.config.get('make_empty_strings_none', True)
            ctx.input = _normalize(ctx.input, strip_strings, make_empty_none)


def _normalize(data, strip_strings, make_empty_none):
    if not strip_strings and not make_empty_none:
        return data

    if data is None:
        return data

    if is_string(data):
        if strip_strings:
            data = data.strip()
        if make_empty_none:
            data = None if data == "" else data

    elif isinstance(data, dict):
        data = dict([
            (k, _normalize(data[k], strip_strings, make_empty_none))
            for k in data.keys()
        ])

    elif isinstance(data, list):
        data = [
            _normalize(v, strip_strings, make_empty_none)
            for v in data
        ]

    return data
