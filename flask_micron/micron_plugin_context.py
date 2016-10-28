"""This module provides the MicronPluginContext class."""

class MicronPluginContext(object):
    """The MicronPluginContext is used to store the data that is required
    for Micron during request processing. This data is used by MicronMethod
    and it is passed on to MicronPlugin hooks.
    """
    def __init__(self):
        self.config = None
        self.function = None
        self.input = None
        self.output = None
        self.error = None
        self.response = None
