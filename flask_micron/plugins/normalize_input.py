# pylint: disable=too-many-branches

"""This module implements an input normalization plugin for Flask-Micron."""
from flask_micron.micron_plugin import MicronPlugin
from flask_micron.compat import is_string


class Plugin(MicronPlugin):
    """An input normalization plugin for Micron.

    Normalizes the request data by:
      - stripping whitespace from the string values;
      - making empty strings None.

    Normalization is applied to:
      - strings
      - dicts (recursively)
      - lists (recursively)

    Configuration options:

      - normalize: True/False (default = True)
        Whether or not to apply normalization to the request.

      - strip_strings: True/False (default = True)
        Whether or not to strip leading and trailing whitespace from strings.

      - make_empty_strings_none: True/False (default = True)
        Whether or not empty strings must be normalized to None.

    Example:

        @micron.method(
            normalize=True,
            strip_strings=False,
            make_empty_strings_none=True)
        def my_method(arg):
            ...
            ...
    """
    def process_input(self, ctx):
        """Normalizes input data.

        Args:
            data: The data to normalize.
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
