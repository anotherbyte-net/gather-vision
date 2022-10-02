"""The main application features."""
import dataclasses
import typing

import importlib_metadata as import_metadata

from gather_vision import model, plugin, utils


@dataclasses.dataclass
class PluginItem:
    """Information about a plugin."""

    entry_point: import_metadata.EntryPoint
    entry_class: typing.Type[plugin.Entry]
    entry_instance: plugin.Entry


class App:
    """The main application."""

    group = "gather_vision.plugin"

    _available: typing.List[PluginItem] = []

    def load(self) -> typing.List[PluginItem]:
        """Collect the available plugins.

        Load the plugin information.

        Returns:
            A list of plugins.
        """
        if not self._available:
            entry_points = self._get_entry_points(self.group)
            for entry_point in entry_points:
                item = self._build_plugin_item(entry_point)
                self._available.append(item)
        return self._available

    def update(self, args: model.UpdateArgs) -> model.UpdateResult:
        """Execute the update action for the plugin with the given name.

        Args:
            args: The update arguments.

        Returns:
            The result of running the plugin's update process.
        """
        named_plugins = [i for i in self.load() if i.entry_point.name == args.name]

        if len(named_plugins) == 1:
            result = named_plugins[0].entry_instance.update(args)
            return result

        if len(named_plugins) == 0:
            raise utils.GatherVisionException(
                f"Could not find plugin named '{args.name}'."
            )

        raise utils.GatherVisionException(
            f"Found multiple plugins named '{args.name}'."
        )

    def list(self, args: model.ListArgs) -> model.ListResult:
        """List all available plugins.

        Args:
            args: The list arguments.

        Returns:
            A list of plugins.
        """
        items = {}
        for plugin_item in self.load():
            result = plugin_item.entry_instance.list(args)
            items.update(result.items)
        return model.ListResult(items)

    def _get_entry_points(self, group: str):
        return import_metadata.entry_points(group=group)

    def _build_plugin_item(self, entry_point: import_metadata.EntryPoint) -> PluginItem:
        entry_class = entry_point.load()
        item = PluginItem(
            entry_point=entry_point,
            entry_class=entry_class,
            entry_instance=entry_class(),
        )
        return item
