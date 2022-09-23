"""Models used by other modules."""
import dataclasses
import typing


@dataclasses.dataclass
class UpdateArgs:
    """The arguments for the update command."""

    name: str


@dataclasses.dataclass
class UpdateResult:
    """The result from the update command."""


@dataclasses.dataclass
class ShowArgs:
    """The arguments for the show command."""

    name: str


@dataclasses.dataclass
class ShowResult:
    """The result from the show command."""


@dataclasses.dataclass
class ListArgs:
    """The arguments for the list command."""


@dataclasses.dataclass
class ListResult:
    """The result from the list command."""

    names: typing.List[str]
