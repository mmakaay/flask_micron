"""This module provides the MicronPluginContext class."""

class MicronPluginContext(object):
    """The MicronPluginContext is used to store the data that is required
    for Micron during request processing. This data is initialized by
    MicronMethod on every request and it is passed on to all MicronPlugin
    hooks.

    For information on the data that are stored in this object, take
    a look at :ref:`user_plugins_context`.
    """
    def __init__(self):
        self.config = None
        self.function = None
        self.input = None
        self.output = None
        self.error = None
        self.response = None
