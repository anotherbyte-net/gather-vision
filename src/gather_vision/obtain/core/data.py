import abc
import dataclasses
import gzip
import json
import logging
import pathlib
import re
import typing

import parsel
import scrapy
from defusedxml.ElementTree import fromstring
from scrapy import crawler
from scrapy import http
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings


logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
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

    body_raw: bytes
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


@dataclasses.dataclass(frozen=True)
class GatherDataItem(abc.ABC):
    """Abstract base class for data items."""

    gather_type: str = dataclasses.field(init=False)
    """The name of this item class."""

    gather_name: str
    """The name of the spider that created this item."""

    tags: dict[str, str]
    """The tag keys and values applied to this data item."""

    def __post_init__(self):
        object.__setattr__(self, "gather_type", self.__class__.__name__)


@dataclasses.dataclass(frozen=True)
class GatherDataRequest(abc.ABC):
    """Abstract base class for data items."""

    url: str
    """The url to request."""

    data: dict
    """The arbitrary data to include in the response."""


class BaseData(abc.ABC):
    """The essential information for an approach to obtaining data."""

    _re_collapse = re.compile(r"[^\S\n\r]+")
    _re_newline = re.compile(r"[\n\r]+")

    def __init__(self):
        self._data: typing.List[GatherDataItem] = []

    @property
    @abc.abstractmethod
    def tags(self) -> dict[str, str]:
        """Get a list of tags applied to this class that obtains data.

        Returns:
            Dictionary of tag keys and values.
        """
        raise NotImplementedError("Must implement 'tags'.")

    def str_collapse(self, value: str) -> str:
        collapsed = self._re_collapse.sub(" ", value)
        newline = self._re_newline.sub("\n", collapsed)
        result = newline.strip()
        return result


class WebData(BaseData, scrapy.Spider, abc.ABC):
    """
    A class that retrieves web data and
    converts it into data items and/or additional urls.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError("Must specify data_descr.")

    @abc.abstractmethod
    def initial_urls(self) -> typing.Iterable[str]:
        """Get the initial urls.

        Returns:
            An iterable of strings.
        """
        raise NotImplementedError("Must implement 'start_requests'.")

    @abc.abstractmethod
    def web_resources(
        self, web_data: WebDataAvailable
    ) -> typing.Iterable[typing.Union[GatherDataRequest, GatherDataItem]]:
        """Parse a web response and provide urls and items.

        Args:
            web_data: The web data available for parsing.

        Returns:
            An iterable of urls and/or data items from the web data.
        """
        raise NotImplementedError("Must implement 'web_resources'.")

    def start_requests(self) -> typing.Iterable[scrapy.Request]:
        """Start the web requests.

        Returns:
            An iterable of requests.
        """
        logger.info("%s: Start", self.__class__.__name__)
        for initial_url in self.initial_urls():
            if initial_url:
                yield scrapy.Request(
                    url=initial_url,
                    callback=self.parse,
                )

    def parse(
        self, response: http.Response, **kwargs
    ) -> typing.Iterable[typing.Union[scrapy.Request, GatherDataItem]]:
        """Parse a web response.

        Args:
            response: A web response.
            **kwargs: Additional arguments.

        Returns:
            An iterable of requests and/or data items.
        """
        content_type_header = response.headers["Content-Type"].decode("utf-8").lower()

        if logger.isEnabledFor(logging.INFO):
            log_response_flags = (
                " [" + ",".join(sorted(response.flags)) + "]" if response.flags else ""
            )
            logger.info(
                "%s: %s%s",
                self.__class__.__name__,
                response.url,
                log_response_flags,
            )

        if isinstance(response, http.TextResponse):
            if "json" in content_type_header:
                body_data = response.json()
            elif "xml" in content_type_header:
                body_data = self._xml_to_data(fromstring(response.text))
            else:
                body_data = None
            body_text = response.text
            selector = response.selector
        else:
            body_text = None
            body_data = None
            selector = None

        web_data = WebDataAvailable(
            request_url=response.request.url,
            request_method=response.request.method,
            response_url=response.url,
            body_text=body_text,
            body_raw=response.body,
            body_data=body_data,
            selector=selector,
            status=response.status,
            headers=response.headers,
            meta=response.cb_kwargs,
        )
        for i in self.web_resources(web_data):
            if i and isinstance(i, GatherDataItem):
                yield i
            elif i and isinstance(i, GatherDataRequest):
                yield scrapy.Request(
                    url=i.url,
                    callback=self.parse,
                    cb_kwargs={**i.data},
                )

    def _xml_to_data(self, item):
        return {
            "attrs": item.attrib,
            "tag": item.tag,
            "tail": item.tail,
            "text": item.text,
            "children": [self._xml_to_data(i) for i in item],
        }


class LocalData(BaseData, abc.ABC):
    """A class that loads local data and converts it into data items."""

    @abc.abstractmethod
    def local_resources(self) -> typing.Iterable[GatherDataItem]:
        """Load local resource and provide  items.

        Returns:
            An iterable of data items.
        """
        raise NotImplementedError("Must implement 'load_resources'.")


class DataLoad:
    """Load data from local and web sources."""

    def run_local(
        self, data_sources: typing.Iterable[LocalData]
    ) -> typing.Iterable[tuple[LocalData, GatherDataItem]]:
        """Obtain data items from local sources.

        Args:
            data_sources: local data sources.

        Returns:
            An iterable where each entry is a local source and data item.
        """
        logger.info("Starting to load data items from local data sources.")

        source_count = 0
        item_count = 0

        for data_source in data_sources:
            source_count += 1
            for data_item in data_source.local_resources():
                item_count += 1
                yield data_source, data_item

        logger.info(
            "Finished loading %s data items from %s local data sources.",
            item_count,
            source_count,
        )

    def run_web(
        self, data_sources: typing.Iterable[typing.Type[WebData]]
    ) -> typing.Iterable[tuple[WebData, GatherDataItem]]:
        """Run the web data to get items, using scrapy.
        Save the feed to a temp file, then read the items back in.

        Args:
            data_sources: Iterable of web sources.

        Returns:
            An iterable where each entry is a web source and data item.
        """
        logger.info("Starting to load data items from web data sources.")

        data_sources_list = list(data_sources)

        settings = get_project_settings()
        settings.set("WEB_DATA_SOURCES", data_sources_list)

        self._run_crawler(settings, data_sources)

        yield from self._load_feed_items(settings)

        logger.info("Finished %s web data sources.", len(data_sources_list))

    def _run_crawler(
        self, settings: Settings, data_sources: typing.Iterable[typing.Type[WebData]]
    ) -> None:
        process = crawler.CrawlerProcess(settings=settings, install_root_handler=True)

        for data_source in data_sources:
            process.crawl(data_source)

        # logging.getLogger("scrapy").setLevel("ERROR")
        # logging.getLogger("py.warnings").setLevel("CRITICAL")

        # the script will block here until the crawling is finished
        process.start()

    def _load_feed_items(self, settings: Settings) -> typing.Iterable[GatherDataItem]:
        # load the feed items
        feed_dir: pathlib.Path = settings.get("FEEDS_FILE_PATH").parent
        feed_dir.mkdir(parents=True, exist_ok=True)

        from gather_vision.obtain.place import available_web_items

        web_items_map = {i.__name__: i for i in available_web_items}

        item_count = 0
        for item in feed_dir.iterdir():
            if not item.is_file():
                continue
            if item.suffixes != [".jsonl", ".gz"]:
                continue

            with gzip.GzipFile(item, "rb") as f:
                for line in f.readlines():
                    data_raw = json.loads(line)
                    gather_type = data_raw.pop("gather_type")
                    found = web_items_map.get(gather_type)
                    if found:
                        item_count += 1
                        yield found(**data_raw)
                    else:
                        yield None

        logger.info("Finished loading %s web data items.", item_count)
