"""The main application features."""
import typing

from importlib_metadata import EntryPoints, entry_points

from gather_vision import model, plugin, utils


class App:
    """The main application."""

    group = "gather_vision.plugin"

    entry_points: typing.Optional[EntryPoints] = None
    plugins: typing.Dict[str, plugin.Entry] = {}

    def collect(self) -> EntryPoints:
        """Collect the available plugins.

        Returns:
            A collection of EntryPoints.
        """
        if self.entry_points is None:
            self.entry_points = entry_points(group=self.group)
        return self.entry_points

    def load(self) -> typing.Dict[str, plugin.Entry]:
        """Load the plugin class for each plugin.

        Returns:
            A list of
        """
        if not self.plugins:
            for entry_point in self.collect():
                self.plugins[entry_point.name] = entry_point.load()
        return self.plugins

    def get(self, name: str) -> typing.Optional[plugin.Entry]:
        """Get the class for a plugin.

        Args:
            name: The name of the plugin.

        Returns:
            The plugin entry class.
        """
        if name in self.plugins:
            return self.plugins[name]

        entry_pts = entry_points(group=self.group, name=name)
        if entry_pts and len(entry_pts) == 1:
            entry_point = entry_pts[0]
            self.plugins[entry_point.name] = entry_point.load()

        return self.plugins.get(name)

    def update(self, args: model.UpdateArgs) -> model.UpdateResult:
        """Execute the update action for the plugin with the given name.

        Args:
            args: The update arguments.

        Returns:
            The result of running the plugin's update process.
        """
        named_plugin = self.plugins.get(args.name)
        if not named_plugin:
            raise utils.GatherVisionException(
                f"Could not find plugin named '{args.name}'."
            )
        result = named_plugin.update(args)
        return result

    def show(self, args: model.ShowArgs) -> model.ShowResult:
        """Execute the show action for the plugin with the given name.

        Args:
            args: The show arguments.

        Returns:
            The details of the plugin.
        """
        named_plugin = self.plugins.get(args.name)
        if not named_plugin:
            raise utils.GatherVisionException(
                f"Could not find plugin named '{args.name}'."
            )
        result = named_plugin.show(args)
        return result

    def list(
        self, args: model.ListArgs  # noqa: U100 pylint: disable=unused-argument
    ) -> model.ListResult:
        """List all available plugins.

        Args:
            args: The list arguments.

        Returns:
            A list of plugins.
        """
        names = []
        for item in self.collect():
            if not item:
                continue
            names.append(item.name)
        result = model.ListResult(sorted(names))
        return result
