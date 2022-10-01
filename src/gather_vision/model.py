"""Models used by other modules."""
import abc
import dataclasses
import typing
import typing_extensions

import parsel


@dataclasses.dataclass
class UpdateArgs:
    """The arguments for the update command."""

    name: str
    """The action name."""

    data_source: typing.Optional[str] = None
    """The plugin data source name."""


@dataclasses.dataclass
class UpdateResult:
    """The result from the update command."""


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


@dataclasses.dataclass
class WebDataAvailable:
    """The web data available for providing new urls and/or items."""

    request_url: str
    """The requested url."""

    request_method: str
    """The method used for the request."""

    response_url: str
    """The url that provided the response."""

    body_text: str
    """The raw response body text."""

    body_data: typing.Optional[typing.List]
    """The structure body data from json or xml."""

    selector: typing.Optional[parsel.Selector]
    """The selector for obtaining parts of the body data."""

    status: int
    """The response status code."""

    headers: dict
    """The response headers."""

    meta: typing.Optional[dict] = None
    """The metadata associated with the request and response."""


class IsDataclass(typing_extensions.Protocol):
    """Allows specifying type to be any dataclass."""

    # the '__dataclass_fields__' attribute is currently (as at 3.8)
    # the most reliable way to determine if something is a dataclass
    __dataclass_fields__: typing.Dict


class WebData(abc.ABC):
    """A class that retrieves web data and converts it into more urls and/or items."""

    @abc.abstractmethod
    def initial_urls(self) -> typing.Iterable[str]:
        """Get the initial urls.

        Returns:
            A stream of string items.
        """
        raise NotImplementedError("Must implement 'initial_urls'.")

    @abc.abstractmethod
    def parse_response(
        self, data: WebDataAvailable
    ) -> typing.Generator[typing.Union[str, IsDataclass], typing.Any, typing.Any]:
        """Parse a web response and provide urls and items.

        Args:
            data: The web data available for parsing.

        Returns:
            Yield urls and/or items from the web data.
        """
        raise NotImplementedError("Must implement 'parse_response'.")
