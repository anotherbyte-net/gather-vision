"""Public api for plugin entry point."""

import abc
import dataclasses
import pathlib
import typing

from gather_vision.plugin import data


@dataclasses.dataclass
class UpdateArgs:
    """The arguments for the update command."""

    name: typing.Optional[str] = None
    """The action name."""

    data_source: typing.Optional[str] = None
    """The plugin data source name."""

    data_path: typing.Optional[pathlib.Path] = None


@dataclasses.dataclass
class UpdateResult:
    """The result from the update command."""

    web_data: typing.List["data.WebData"]
    local_data: typing.List["data.LocalData"]


@dataclasses.dataclass
class ListArgs:
    """The arguments for the list command."""

    name: typing.Optional[str] = None
    """The plugin name."""

    data_source: typing.Optional[str] = None
    """The plugin data source name."""


@dataclasses.dataclass
class ListResult:
    """The result from the list command."""

    items: typing.Dict[str, typing.List[str]]
    """The map of plugin name and data sources."""


class Entry(abc.ABC):
    """The entry point class for plugins.

    Compatible plugins must implement this class.
    """

    @abc.abstractmethod
    def update(self, args: UpdateArgs) -> UpdateResult:  # noqa: U100
        """Update the data sources that match the args.

        Args:
            args: The arguments for update.

        Returns:
            The result of the update action.
        """
        raise NotImplementedError("Must implement 'update'.")

    @abc.abstractmethod
    def list(self, args: ListArgs) -> ListResult:  # noqa: U100
        """List the plugins and data sources that match the args.

        Args:
            args: The arguments for list.

        Returns:
            The result of the list action.
        """
        raise NotImplementedError("Must implement 'list'.")
