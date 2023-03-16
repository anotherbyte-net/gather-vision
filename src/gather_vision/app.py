"""The main application features."""

import dataclasses
import logging
import pickle
import typing

import scrapy
import importlib_metadata
from scrapy import crawler, exporters, http

from gather_vision import utils
from gather_vision.plugin import data, entry

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class PluginItem:
    """Information about a plugin."""

    entry_point: importlib_metadata.EntryPoint
    entry_class: typing.Type[entry.Entry]
    entry_instance: entry.Entry


class AppPickleItemExporter(exporters.BaseItemExporter):
    def __init__(self, file, protocol=4, **kwargs):
        super().__init__(**kwargs)
        self.file = file
        self.protocol = protocol

    def export_item(self, item):
        d = item
        pickle.dump(d, self.file, self.protocol)


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

            logger.info("Loaded %s plugins.", len(self._available))
        return self._available

    def update(self, args: entry.UpdateArgs) -> entry.UpdateResult:
        """Execute the update action for all plugins or the plugin with the given name.

        Args:
            args: The update arguments.

        Returns:
            The result of running the plugin's update process.
        """
        loaded_plugins = list(self.load())
        named_plugins = [
            i
            for i in loaded_plugins
            if args.name is None or i.entry_point.name == args.name
        ]
        available_plugins = ", ".join(
            sorted(i.entry_point.name for i in loaded_plugins)
        )

        named_count = len(named_plugins)
        available_count = len(loaded_plugins)

        if named_count == 0:
            raise utils.GatherVisionException(
                f"Could not find plugin named '{args.name}'. "
                f"Available plugins ({available_count}): {available_plugins}."
            )

        if args.name and named_count > 1:
            raise utils.GatherVisionException(
                f"Found multiple plugins named '{args.name}'."
                f"Available plugins ({available_count}): {available_plugins}."
            )

        # get the data sources
        local_data: typing.List[data.LocalData] = []
        web_data: typing.List[data.WebData] = []
        for named_plugin in named_plugins:
            plugin_update_result = named_plugin.entry_instance.update(args)

            # load data from local sources
            for local_data_item in plugin_update_result.local_data:
                local_data_item.data = list(local_data_item.load_resources())
            local_data.extend(plugin_update_result.local_data)

            # get the web data sources
            web_data.extend(plugin_update_result.web_data)

        logger.info("Loaded %s local data sources.", len(local_data))

        # allow running multiple plugins at once
        # run the spider
        logger.info("Starting %s web data sources.", len(web_data))
        web_data_map = dict([(self._data_item_id(i), i) for i in web_data])

        # build the output paths

        if not args.data_path:
            raise ValueError(f"Invalid data path '{args.data_path}'.")

        feed_path = args.data_path / "feeds" / "feed_%(name)s_%(time)s.pickle"
        feed_path_setting = str(feed_path).replace("\\", "/")

        files_dir = args.data_path / "files"
        files_dir_setting = str(files_dir).replace("\\", "/")

        http_cache_dir = args.data_path / "http_cache"
        http_cache_dir_setting = str(http_cache_dir).replace("\\", "/")

        # run the web data to get items, using scrapy
        # save the feed to a temp file, then read the items back in
        process = crawler.CrawlerProcess(
            settings={
                "USER_AGENT": "gather-vision (+https://github.com/anotherbyte-net/gather-vision)",
                # http cache
                "HTTPCACHE_ENABLED": True,
                "HTTPCACHE_DIR": http_cache_dir_setting,
                "HTTPCACHE_POLICY": "scrapy.extensions.httpcache.DummyPolicy",
                "HTTPCACHE_STORAGE": "scrapy.extensions.httpcache.FilesystemCacheStorage",
                "EXTENSIONS": {
                    "scrapy.extensions.telnet.TelnetConsole": None,
                },
                # feed
                "FEED_EXPORTERS": {
                    "pickle_raw": "gather_vision.app.AppPickleItemExporter",
                },
                "FEEDS": {
                    f"file:///{feed_path_setting}": {"format": "pickle_raw"},
                },
                "WEB_DATA_ITEMS": web_data,
                # logs
                "LOG_ENABLED": True,
                "LOG_FILE": None,
                "LOG_STDOUT": False,
                "LOG_LEVEL": "ERROR",
                # throttling requests
                "DOWNLOAD_DELAY": 3,
                "AUTOTHROTTLE_ENABLED": True,
                "AUTOTHROTTLE_START_DELAY": 3,
                "AUTOTHROTTLE_MAX_DELAY": 60,
                "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
                # pipelines
                "ITEM_PIPELINES": {
                    "scrapy.pipelines.files.FilesPipeline": 1,
                },
                "FILES_STORE": files_dir_setting,
                "MEDIA_ALLOW_REDIRECTS": True,
                # Set settings whose default value is deprecated to a future-proof value
                "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
                "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
                "FEED_EXPORT_ENCODING": "utf-8",
            },
            install_root_handler=True,
        )

        process.crawl(WebDataFetch)

        logging.getLogger("scrapy").setLevel("ERROR")
        logging.getLogger("py.warnings").setLevel("CRITICAL")

        # the script will block here until the crawling is finished
        process.start()

        # load the feed items
        feed_item_count = 0
        for item in feed_path.parent.iterdir():
            if not item.is_file():
                continue
            if item.suffix != ".pickle":
                continue

            with item.open("rb") as f:
                while True:
                    try:
                        # store PluginDataItems in the related PluginWebData instance
                        web_data_item = pickle.load(f)
                        map_id = self._data_item_id(web_data_item)
                        web_data_map[map_id].data = [web_data_item]
                        feed_item_count += 1
                    except EOFError:
                        break

        logger.info("Loaded %s data items from web data sources.", feed_item_count)
        logger.info("Finished update.")

        return entry.UpdateResult(web_data=web_data, local_data=local_data)

    def list(self, args: entry.ListArgs) -> entry.ListResult:
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
        return entry.ListResult(items)

    def _get_entry_points(self, group: str):
        return importlib_metadata.entry_points(group=group)

    def _build_plugin_item(
        self, entry_point: importlib_metadata.EntryPoint
    ) -> PluginItem:
        entry_class = entry_point.load()
        item = PluginItem(
            entry_point=entry_point,
            entry_class=entry_class,
            entry_instance=entry_class(),
        )
        return item

    def _data_item_id(self, item) -> str:
        return "-".join([item.plugin_name, item.plugin_data_source])


class WebDataFetch(scrapy.Spider):
    name = "web-data"

    def start_requests(self):
        web_data_items: typing.List[data.WebData] = self.settings.get("WEB_DATA_ITEMS")
        for web_data_item in web_data_items:
            for initial_url in web_data_item.initial_urls():
                yield scrapy.Request(
                    url=initial_url,
                    callback=self.parse,
                    cb_kwargs={"web_data_item": web_data_item},
                )

    def parse(self, response: http.Response, **kwargs):
        web_data_item: data.WebData = response.cb_kwargs.get("web_data_item")

        is_json = "json" in response.headers["Content-Type"].decode("utf-8").lower()

        if isinstance(response, http.TextResponse):
            body_data = response.json() if is_json else None
            selector = response.selector
        else:
            body_data = None
            selector = None

        web_data = data.WebDataAvailable(
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
        for i in web_data_item.parse_response(web_data):
            if isinstance(i, str):
                yield scrapy.Request(
                    url=i,
                    callback=self.parse,
                    cb_kwargs={"web_data_item": web_data_item},
                )
            else:
                yield i
