import abc
import dataclasses
import logging
import pickle
import typing

import parsel
import scrapy
from defusedxml.ElementTree import fromstring
from scrapy import crawler, exporters
from scrapy import http
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)


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


class BaseData(abc.ABC):
    """The essential information for an approach to obtaining data."""

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


class WebData(BaseData, abc.ABC):
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


class LocalData(BaseData, abc.ABC):
    """A class that loads local data and converts it into data items."""

    @abc.abstractmethod
    def local_resources(self) -> typing.Iterable[GatherDataItem]:
        """Load local resource and provide  items.

        Returns:
            An iterable of data items.
        """
        raise NotImplementedError("Must implement 'load_resources'.")


class WebDataFetch(scrapy.Spider):
    """Fetch items from data sources."""

    name = "web-data"

    def start_requests(self) -> typing.Iterable[scrapy.Request]:
        """Start the web requests.

        Returns:
            An iterable of requests.
        """
        data_sources: typing.List[WebData] = self.settings.get("WEB_DATA_SOURCES")
        for data_source in data_sources:
            logger.info("Starting %s", type(data_source).__name__)
            for initial_url in data_source.initial_urls():
                if initial_url:
                    yield scrapy.Request(
                        url=initial_url,
                        callback=self.parse,
                        cb_kwargs={"web_data_source": data_source},
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
        data_source: WebData = response.cb_kwargs.get("web_data_source")
        content_type_header = response.headers["Content-Type"].decode("utf-8").lower()

        logger.info(
            "Response for %s: %s",
            type(data_source).__name__,
            response.url,
        )

        if isinstance(response, http.TextResponse):
            if "json" in content_type_header:
                body_data = response.json()
            elif "xml" in content_type_header:
                body_data = fromstring(response.text)
            else:
                body_data = None
            selector = response.selector
        else:
            body_data = None
            selector = None

        web_data = WebDataAvailable(
            request_url=response.request.url,
            request_method=response.request.method,
            response_url=response.url,
            body_text=response.text,
            body_data=body_data,
            selector=selector,
            status=response.status,
            headers=response.headers,
            meta=response.cb_kwargs,
        )
        for i in data_source.web_resources(web_data):
            if i is None:
                yield None
            elif i and isinstance(i, str):
                yield scrapy.Request(
                    url=i,
                    callback=self.parse,
                    cb_kwargs={"web_data_source": data_source},
                )
            else:
                yield i


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
        self, data_sources: typing.Iterable[WebData]
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

        process = crawler.CrawlerProcess(settings=settings, install_root_handler=False)

        process.crawl(WebDataFetch)

        logging.getLogger("scrapy").setLevel("ERROR")
        logging.getLogger("py.warnings").setLevel("CRITICAL")

        # the script will block here until the crawling is finished
        process.start()

        # load the feed items
        feed_path = settings.get("FEEDS_FILE_PATH")
        feed_path.parent.mkdir(parents=True, exist_ok=True)
        item_count = 0
        for item in feed_path.parent.iterdir():
            if not item.is_file():
                continue
            if item.suffix != ".pickle":
                continue

            with item.open("rb") as f:
                while True:
                    try:
                        data_item = pickle.load(f)
                        item_count += 1
                        yield data_item
                    except EOFError:
                        break

        logger.info(
            "Finished loading %s data items from %s web data sources.",
            item_count,
            len(data_sources_list),
        )


class AppPickleItemExporter(exporters.BaseItemExporter):
    def __init__(self, file, protocol=4, **kwargs):
        super().__init__(**kwargs)
        self.file = file
        self.protocol = protocol

    def export_item(self, item):
        d = item
        pickle.dump(d, self.file, self.protocol)
