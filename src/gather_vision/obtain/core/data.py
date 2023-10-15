import abc
import dataclasses
import gzip
import json
import logging
import pathlib
import re
import typing
from datetime import datetime
import zoneinfo
from urllib.parse import urljoin

import parsel
import scrapy

from django.conf import settings as proj_django_settings
from django.utils.dateparse import parse_datetime
from itemadapter import ItemAdapter
from scrapy import crawler as scrapy_crawler, http, settings as scrapy_settings
from scrapy.utils.project import get_project_settings
from twisted.internet.defer import Deferred

from gather_vision.obtain.core.utils import xml_to_data

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

    body_data: list | dict | None
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
    """Abstract base class for data items.

    Used to store data after being extracted from web responses.

    Then, :meth:`save_models` can be used in the Item Pipeline to
    save the models to the database.
    """

    gather_name: str
    """The name of the spider that created this item."""

    gather_type: str = dataclasses.field(init=False)
    """The name of this item class."""

    def __post_init__(self):
        object.__setattr__(self, "gather_type", self.__class__.__name__)

    @abc.abstractmethod
    async def save_models(self) -> None:
        """Save models equivalent to the dataclass to the database.

        Returns:
            None
        """
        raise NotImplementedError()

    @classmethod
    def datetime_parse(
        cls, value: str, timezone: str, formats: list[str] | None = None
    ) -> datetime | None:
        value = (value or "").strip()
        if not value:
            return None

        tz = zoneinfo.ZoneInfo(timezone)

        options = [
            *(formats or []),
            "%d/%m/%Y %I:%M %p",
            "%I:%M %p",
            "%a, %d %b %Y %H:%M:%S %z",
            "%d/%m/%Y",
        ]
        for option in options:
            try:
                return datetime.strptime(value, option).replace(tzinfo=tz)
            except ValueError:
                continue

        logger.warning("Cannot parse '%s' using %s.", value, options)

        try:
            parsed = parse_datetime(value)
            if parsed:
                return parsed.replace(tzinfo=tz)
        except ValueError:
            pass

        raise ValueError(f"Cannot parse datetime '{value}'.")

    @classmethod
    def datetime_now(cls, timezone: str) -> datetime:
        return datetime.now().replace(tzinfo=zoneinfo.ZoneInfo(timezone))


@dataclasses.dataclass(frozen=True)
class GatherDataRequest(abc.ABC):
    """Abstract base class for data items."""

    url: str
    """The url to request."""

    data: dict
    """The arbitrary data to include in the response."""


@dataclasses.dataclass(frozen=True)
class GatherDataOrigin:
    title: str
    description: str
    url: str
    areas: typing.Iterable["GatherDataArea"]


@dataclasses.dataclass(frozen=True, order=True)
class GatherDataArea:
    level: str
    title: str
    parent: typing.Optional["GatherDataArea"] = None


@dataclasses.dataclass(frozen=True)
class GatherDataContainerCheck:
    label: str
    required_one: list[str] | typing.Callable[[str], bool] | None = None
    required_all: list[str] | typing.Callable[[str], bool] | None = None
    forbidden: list[str] | typing.Callable[[str], bool] | None = None
    allowed: list[str] | typing.Callable[[str], bool] | None = None
    allow_unmatched: bool = False

    def check(self, entries: typing.Iterable[str]) -> bool:
        if not entries or not [i for i in entries if i]:
            return False
        forb = self.forbidden
        reqa = self.required_all
        rqeo = self.required_one
        allo = self.allowed

        entry_set = set(entries)

        # check forbidden items first
        if forb and isinstance(forb, typing.Iterable):
            if entry_set.intersection(set(forb)):
                return False
        if forb and isinstance(forb, typing.Callable):
            if any(forb(entry) for entry in entry_set):
                return False

        # ensure all required items are present
        if reqa and isinstance(reqa, typing.Iterable):
            if not all(reqa_item in entry_set for reqa_item in reqa):
                return False
        if reqa and isinstance(reqa, typing.Callable):
            if not all(reqa(entry) for entry in entry_set):
                return False

        # ensure at least one item is present
        if rqeo and isinstance(rqeo, typing.Iterable):
            if not any(rqeo_item in entry_set for rqeo_item in rqeo):
                return False
        if rqeo and isinstance(rqeo, typing.Callable):
            if not any(rqeo(entry) for entry in entry_set):
                return False

        # if unmatched items are not allowed, check all other items are allowed
        if not self.allow_unmatched:
            if allo and isinstance(allo, typing.Iterable):
                if not all(allo_item in entry_set for allo_item in allo):
                    return False
            if allo and isinstance(allo, typing.Callable):
                if not all(allo(entry) for entry in entry_set):
                    return False
        return True


class BaseData(abc.ABC):
    """The essential information for an approach to obtaining data."""

    _re_collapse = re.compile(r"[^\S\n\r]+")
    _re_newline = re.compile(r"[\n\r]+")

    def __init__(self):
        self._data: typing.List[GatherDataItem] = []

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
            if "json" in content_type_header or response.url.endswith(".json"):
                body_data = response.json()
            elif "xml" in content_type_header:
                body_data = xml_to_data(response.text)
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
            elif i is None:
                pass
            else:
                raise ValueError(i)

    def _make_abs_url(self, base: str, suffix: str) -> str:
        # https://results.ecq.qld.gov.au/elections/
        # state/State2017/results/summary.html
        return urljoin(base, suffix)


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

        # self._combine_feed_items(settings)

        for i in []:
            yield None, None
        # yield from self._load_feed_items(settings)

        logger.info("Finished %s web data sources.", len(data_sources_list))

    def _run_crawler(
        self,
        settings: scrapy_settings.Settings,
        data_sources: typing.Iterable[typing.Type[WebData]],
    ) -> None:
        """Run the Scrapy crawler.

        Args:
            settings: The scrapy Settings.
            data_sources: Zero or more WebData instances.

        Returns:
            None
        """
        process = scrapy_crawler.CrawlerProcess(
            settings=settings, install_root_handler=True
        )

        for data_source in data_sources:
            process.crawl(data_source)

        # logging.getLogger("scrapy").setLevel("ERROR")
        # logging.getLogger("py.warnings").setLevel("CRITICAL")

        # the script will block here until the crawling is finished
        process.start()

    def _load_feed_items(
        self, settings: scrapy_settings.Settings
    ) -> typing.Iterable[GatherDataItem]:
        """Load feed items from the files created by scrapy.

        Args:
            settings:  The scrapy Settings.

        Returns:
            Zero or more GatherDataItem instances.
        """
        # load the feed items
        feed_dir: pathlib.Path = settings.get("FEEDS_FILE_PATH").parent
        feed_dir.mkdir(parents=True, exist_ok=True)

        item_count = 0
        for item in feed_dir.iterdir():
            if not item.is_file():
                continue
            if item.suffixes != [".jsonl", ".gz"]:
                continue
            if not item.stem.startswith("web-data-"):
                continue

            for web_data_item in self._read_jsonl_gz_file(item):
                if web_data_item:
                    item_count += 1
                    yield web_data_item
                else:
                    yield None

        logger.info("Finished loading %s web data items.", item_count)

    def _combine_feed_items(self, settings: scrapy_settings.Settings) -> None:
        """Combine Scrapy feed files into per-WebData files.

        Args:
            settings:  The scrapy Settings.

        Returns:
            None
        """
        # load the feed items
        feed_dir: pathlib.Path = settings.get("FEEDS_FILE_PATH").parent
        feed_dir.mkdir(parents=True, exist_ok=True)

        # load gather data items

        web_data_items = {}
        for item in feed_dir.iterdir():
            if not item.is_file():
                continue
            if item.suffixes != [".jsonl", ".gz"]:
                continue

            parts = item.stem.split("_")
            if len(parts) != 3:
                continue

            web_data_name = parts[1]

            if web_data_name not in web_data_items:
                web_data_items[web_data_name] = set()

            count_before = len(web_data_items[web_data_name])
            for web_data_item in self._read_jsonl_gz_file(item):
                # TODO: unhashable type list - need some way to compare dataclass instances
                web_data_items[web_data_name].add(web_data_item)
            count_after = len(web_data_items[web_data_name])

            # delete any empty files
            if count_after - count_before < 1:
                item.unlink()

        # add gather data items to per-WebData files
        for web_data_name, items in web_data_items.items():
            logger.info("Combining data for %s", web_data_name)
            web_data_file = feed_dir / f"web-data-{web_data_name}.jsonl.gz"
            web_data_combined = set()
            if web_data_file.exists():
                for item in self._read_jsonl_gz_file(web_data_file):
                    web_data_combined.add(item)
            count_existing = len(web_data_combined)
            logger.info("%s existing items", count_existing)

            for item in items:
                web_data_combined.add(item)
            count_new = len(web_data_combined) - count_existing
            logger.info("%s new items", count_new)

            self._write_jsonl_gz_file(web_data_file, web_data_combined)

    def _read_jsonl_gz_file(
        self, path: pathlib.Path
    ) -> typing.Iterable[GatherDataItem]:
        from gather_vision.obtain.place import available_web_items

        web_items_map = {i.__name__: i for i in available_web_items}

        seen_count = 0
        known_count = 0
        unknown_count = 0
        with gzip.GzipFile(path, "rb") as f:
            for line in f.readlines():
                for data_raw in self._load_json(line):
                    built_item = self._restore_data_item(web_items_map, data_raw)
                    seen_count += 1
                    if built_item:
                        known_count += 1
                        yield built_item
                    else:
                        unknown_count += 1

        logger.info(
            "Found %s total items, %s known, %s unknown, in %s",
            seen_count,
            known_count,
            unknown_count,
            path,
        )

        if unknown_count > 0:
            msg = f"Found {unknown_count} unknown items of {seen_count} in {path}."
            raise ValueError(msg)

    def _write_jsonl_gz_file(
        self, path: pathlib.Path, items: typing.Iterable[GatherDataItem]
    ) -> None:
        with gzip.GzipFile(path, "wb") as f:
            lines = [
                json.dumps(dataclasses.asdict(item), sort_keys=True).encode(
                    encoding="utf-8"
                )
                for item in sorted(items, key=lambda x: (x.gather_type, x.gather_name))
            ]
            f.writelines(lines)

    def _restore_data_item(
        self, web_items_map: dict, raw: dict
    ) -> typing.Optional[GatherDataItem]:
        gather_type = raw.pop("gather_type")
        found = web_items_map.get(gather_type)
        if not found:
            return None

        bad_kwarg_msg = "got an unexpected keyword argument"
        missing_arg_msg = "required positional arguments"
        while True:
            try:
                return found(**raw)
            except TypeError as e:
                err_msg = str(e)
                if bad_kwarg_msg in err_msg:
                    kw_name = err_msg.split(bad_kwarg_msg)[-1].strip("' ")
                    raw.pop(kw_name)
                elif missing_arg_msg in err_msg:
                    raise NotImplementedError()
                else:
                    raise NotImplementedError()

    def _load_json(self, raw: bytes | typing.Iterable[bytes]) -> typing.Iterable[dict]:
        sep = b'"}{"'
        if isinstance(raw, bytes):
            raw = [raw]

        # fix jsonl without newlines between entries
        lines = []
        for el1 in raw:
            if sep in el1:
                for el2 in el1.replace(b'"}{"', b'"}\t\f\n{"').split(b"\t\f\n"):
                    lines.append(el2)
            else:
                lines.append(el1)

        # try to read the json
        for line in lines:
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                context = raw[max(0, e.pos - 2) : min(len(line), e.pos + 2)]
                msg = f"Failed reading json string at {context}."
                raise ValueError(msg) from e


class GatherVisionStoreDjangoItemPipeline:
    """Store items in a Django database."""

    def __init__(self, proj_settings):
        self._proj_settings = proj_settings

    @classmethod
    def from_crawler(
        cls, crawler: scrapy_crawler.Crawler
    ) -> "GatherVisionStoreDjangoItemPipeline":
        return cls(proj_django_settings)

    def open_spider(self, spider: scrapy.Spider) -> None:
        pass

    def close_spider(self, spider: scrapy.Spider) -> None:
        pass

    async def process_item(
        self,
        item: scrapy.Item | dict | IsDataclass | GatherDataItem,
        spider: scrapy.Spider,
    ) -> scrapy.Item | dict | IsDataclass | GatherDataItem | Deferred:
        if not ItemAdapter.is_item(item):
            raise ValueError("Not a scrapy item %s", item)

        # item_adapted = ItemAdapter(item)

        if not isinstance(item, GatherDataItem):
            return item

        # if the item is a GatherDataItem, save it
        await item.save_models()

        return item
