"""This module provides the MicronPluginContainer class."""

from flask_micron import micron_plugin_compiler


class MicronPluginContainer(object):
    """The MicronPluginContainer class well... contains MicronPlugins.
    It is used by Micron to register plugins and to execute hook
    functions from those plugins.
    """
    def __init__(self, *plugins):
        r"""Creates a new MicronPluginContainer object.

        :param \*plugins:
            Plugins to add to the container directly. Additional plugins can
            be added after construction using the method add(\*plugin)".
        """
        self._plugins = []
        self._hook_functions = {}
        self.add(*plugins)

    def add(self, *plugins):
        r"""Add MicronPlugins to this MicronPluginContainer.

        :param \*plugins:
            The plugin(s) to add.
        """
        for plugin in plugins:
            self._compile_plugin(plugin)
            self._plugins.append(plugin)

    def _compile_plugin(self, plugin):
        hooks = micron_plugin_compiler.compile(plugin)
        for hook, hook_function in hooks.items():
            self._hook_functions.setdefault(hook, []).append(hook_function)

    def call_all(self, context, hook):
        """Call the hook function in all registered plugins.

        :param MicronPluginContext context:
            The MicronPluginContext to pass to the plugins.
        :param string hook:
            The name of the hook function to call.
        """
        if hook in self._hook_functions:
            for hook_function in self._hook_functions[hook]:
                hook_function(context)

    def call_one(self, context, hook):
        """Call the hook function in the latest registered plugin
        that implements the hook function.

        :param MicronPluginContext context:
            The MicronPluginContext to pass to the plugins.
        :param string hook:
            The name of the hook function to call.
        """
        try:
            hook_function = self._hook_functions[hook][-1]
            hook_function(context)
        except KeyError:
            pass

    def __contains__(self, type_or_instance):
        """Checks if the plugin container contains a given plugin
        type or instance.

        Example::

            >>> class MyPlugin(MicronPlugin): pass
            >>> my = MyPlugin()
            >>> container = MicronPluginContainer()
            >>> container.add(my)
            >>> my in container
            True
            >>> MyPlugin in container
            True
            >>> my2 = MyPlugin()
            >>> my2 in container
            False
        """
        if isinstance(type_or_instance, type):
            return any([
                p for p in self._plugins
                if isinstance(p, type_or_instance)
            ])
        else:
            return type_or_instance in self._plugins
