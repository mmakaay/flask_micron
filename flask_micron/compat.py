# pylint: disable=redefined-outer-name, pointless-statement

"""This module contains code that is needed to make Flask-Micron work for
both Python v2 and Python v3."""

def is_string(value):
    """Check if a value is a string.

    :param value: The value to check.

    :returns:
        True in case the provided value is a string, False otherwise.
    """
    try:
        basestring
        def is_string(value):
            """Python 2 compatible implementation of is_string(value)."""
            return isinstance(value, basestring)
    except NameError:
        def is_string(value):
            """Python 3 compatible implementation of is_string(value)."""
            return isinstance(value, (str, bytes))
    return is_string(value)
