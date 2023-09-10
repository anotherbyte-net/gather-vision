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
    """Abstract base class for data items."""

    tags: dict[str, str]
    """The tag keys and values applied to this data item."""


class GetData(abc.ABC):
    """The essential information for an approach to obtaining data."""

    def __init__(self):
        self._data: typing.List[GatherDataItem] = []

    @abc.abstractmethod
    @property
    def tags(self) -> dict[str, str]:
        """Get a list of tags applied to this class that obtains data.

        Returns:
            Dictionary of tag keys and values.
        """
        raise NotImplementedError("Must implement 'tags'.")


class WebData(GetData, abc.ABC):
    """
    A class that retrieves web data and
    converts it into data items and/or additional urls.
    """

    @abc.abstractmethod
    def initial_urls(self) -> typing.Iterable[str]:
        """Get the initial urls.

        Returns:
            An iterable of strings.
        """
        raise NotImplementedError("Must implement 'initial_urls'.")

    @abc.abstractmethod
    def web_resources(
        self, web_data: WebDataAvailable
    ) -> typing.Iterable[typing.Union[str, GatherDataItem]]:
        """Parse a web response and provide urls and items.

        Args:
            web_data: The web data available for parsing.

        Returns:
            An iterable of urls and/or data items from the web data.
        """
        raise NotImplementedError("Must implement 'web_resources'.")


class LocalData(GetData, abc.ABC):
    """A class that loads local data and converts it into data items."""

    @abc.abstractmethod
    def local_resources(self) -> typing.Iterable[GatherDataItem]:
        """Load local resource and provide  items.

        Returns:
            An iterable of data items.
        """
        raise NotImplementedError("Must implement 'load_resources'.")
