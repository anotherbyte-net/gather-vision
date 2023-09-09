import abc
import dataclasses
import typing

import parsel


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


class IsDataclass(typing.Protocol):
    """Allows specifying type to be any dataclass."""

    # the '__dataclass_fields__' attribute is (as at Python 3.8)
    # the most reliable way to determine if something is a dataclass
    __dataclass_fields__: typing.Dict


@dataclasses.dataclass
class GatherDataItem(abc.ABC):
    """Abstract base class for gather vision data items."""

    plugin_name: str
    """The plugin name that provides the data item implementation."""

    plugin_data_source: str
    """The name of the plugin data source that populates this data item."""

    # data_item_reference: str
    # """The full qualified name to this data item."""


class GetData(abc.ABC):
    """A way to obtain data."""

    @abc.abstractmethod
    @property
    def tags(self) -> list[str]:
        """Get a list of tags applied to this class that obtains data."""
        raise NotImplementedError("Must implement 'tags'.")


class WebData(abc.ABC):
    """A class that retrieves web data and converts it into more urls and/or items."""

    def __init__(self, plugin_name: str, plugin_data_source: str):
        self.plugin_name = plugin_name
        self.plugin_data_source = plugin_data_source
        self._data: typing.List[GatherDataItem] = []

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: typing.Optional[typing.List[GatherDataItem]]):
        if value is None:
            self._data = []
        else:
            self._data.extend(value)

    @abc.abstractmethod
    def initial_urls(self) -> typing.Iterable[str]:
        """Get the initial urls.

        Returns:
            A stream of string items.
        """
        raise NotImplementedError("Must implement 'initial_urls'.")

    @abc.abstractmethod
    def parse_response(
        self, data: WebDataAvailable  # noqa: U100
    ) -> typing.Generator[typing.Union[str, GatherDataItem], typing.Any, typing.Any]:
        """Parse a web response and provide urls and items.

        Args:
            data: The web data available for parsing.

        Returns:
            Yield urls and/or items from the web data.
        """
        raise NotImplementedError("Must implement 'parse_response'.")


class LocalData(abc.ABC):
    def __init__(self, plugin_name: str, plugin_data_source: str):
        self.plugin_name = plugin_name
        self.plugin_data_source = plugin_data_source
        self._data: typing.List[GatherDataItem] = []

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: typing.Optional[typing.List[GatherDataItem]]):
        if value is None:
            self._data = []
        else:
            self._data.extend(value)

    @abc.abstractmethod
    def load_resources(
        self,
    ) -> typing.Generator[GatherDataItem, typing.Any, typing.Any]:
        """Load local resource and provide  items.

        Returns:
            Yield items from the local data.
        """
        raise NotImplementedError("Must implement 'load_resources'.")
