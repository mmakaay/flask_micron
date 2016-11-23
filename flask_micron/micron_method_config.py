# -*- coding: utf-8 -*-
"""This module provides the MicronMethodConfiguration class."""

import re
from flask_micron.errors import ImplementationError


class MicronMethodConfig(object):
    """This class encapsulates the configuration options that are used
    for executing a MicronMethod.

    Within Micron, this configuration is peformed at two levels:

    - The Micron-level configuration (defined by calling the method
      Micron.configure() on a Micron instance)
    - The MicronMethod-level configuration (defined by options that were
      used in the @micron.method() decorator)

    This class supports this multi-level configuration by making each
    MicronMethodConfig aware of its parent configuration (so basically,
    we create a linked list of configurations).

    Example:

        >>> level1 = MicronMethodConfig(x=False, y=True)
        >>> level2 = MicronMethodConfig(level2, x=True, y=True)
        >>> level3 = MicronMethodConfig(level3, y=None)
        >>> level1.x
        False
        >>> level2.x
        True
        >>> level3.x
        True
        >>> level2.y
        True
        >>> level3.y
        None
    """

    IDENTIFIER_FORMAT = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')

    def __init__(self, parent=None, **configuration):
        r"""Creates a new MicronMethodConfig.

        :param MicronMethodConfig parent:
            The parent of this MicronMethodConfig object.
        :param \**configuration:
            Values to instantiate this config object with.
        """
        # Using the super __setattr__ is required to prevent endless loops,
        # since we implemented __setattr__/__getattr__ for this class.
        setmyattr = super(MicronMethodConfig, self).__setattr__
        setmyattr('_parent', parent)
        setmyattr('_data', {})

        self.configure(**configuration)

    def __call__(self, **configuration):
        return self.configure(**configuration)

    def configure(self, **configuration):
        r"""Set configuration values for this config object.

        :param \**configuration:
            Values to update this config object with.

        :returns:
            The MicronMethodConfig itself, useful for fluent syntax.
        """
        for name, value in configuration.items():
            self.set(name, value)
        return self

    def __getattr__(self, name):
        """For making config options available as instance attributes
        of the config object.
        """
        return self.get(name)

    def __setattr__(self, name, value):
        """For making config options available as instance attributes
        of the config object.
        """
        self.set(name, value)

    def set(self, name, value):
        """Set a configuration option by name.

        :param string name:
            The name of the configuration option.
        :param value:
            The value to set it to.
        """
        self._check_option_name(name)
        self._data[name] = value

    def _check_option_name(self, name):
        if not self.IDENTIFIER_FORMAT.match(name):
            raise ImplementationError(
                "Invalid configuration option name '%s' used "
                "(only lowercase letters, numbers and underscores are allowed "
                "and the name must start with a letter)" % name)

    @property
    def option_names(self):
        """Returns a set of all configuration option names that are currently
        in use in the MicronMethodConfig hierarchy.
        """
        names = set()
        parent = self
        while parent is not None:
            names.update(parent._data.keys())
            parent = parent._parent
        return names

    @property
    def flattened(self):
        """Returns a dict of all configuration options that are currently
        in use in the MicronMethodConfig hierarchy.

        :returns:
            A dict, containing all configuration options.
        """
        flattened = dict(self._data)
        parent = self._parent
        while parent:
            for name, value in parent._data.items():
                flattened.setdefault(name, value)
            parent = parent._parent
        return flattened


    def get(self, name):
        """Retrieve a configuration value by name.

        When this MicronMethodConfig object does not have a value for the
        requested configuration option, then the parent config will be
        consulted. When no parent config exists, a KeyError is raised.

        :param string name:
            The name of the configuration value to retrieve.

        :returns:
            The configuration value.
        """
        if name in self._data:
            return self._data[name]
        if self._parent is None:
            raise KeyError(
                "No value defined for configuration option '%s'" % name)
        return self._parent.get(name)
