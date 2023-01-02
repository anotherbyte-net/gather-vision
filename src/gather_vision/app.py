"""The main application features."""
import dataclasses
import logging
import pathlib
import pickle
import tempfile
import typing

import scrapy
from importlib_metadata import EntryPoint, entry_points
from scrapy.crawler import CrawlerProcess
from scrapy.exporters import BaseItemExporter
from scrapy.http import Response, TextResponse

from gather_vision import utils
from gather_vision.plugin import data as plugin_data, entry as plugin_entry

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class PluginItem:
    """Information about a plugin."""

    entry_point: EntryPoint
    entry_class: typing.Type[plugin_entry.Entry]
    entry_instance: plugin_entry.Entry


class AppPickleItemExporter(BaseItemExporter):
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

    def update(self, args: plugin_entry.UpdateArgs) -> plugin_entry.UpdateResult:
        """Execute the update action for all plugins or the plugin with the given name.

        Args:
            args: The update arguments.

        Returns:
            The result of running the plugin's update process.
        """
        named_plugins = [
            i
            for i in self.load()
            if args.name is None or i.entry_point.name == args.name
        ]

        if len(named_plugins) == 0:
            raise utils.GatherVisionException(
                f"Could not find plugin named '{args.name}'."
            )

        if args.name and len(named_plugins) > 1:
            raise utils.GatherVisionException(
                f"Found multiple plugins named '{args.name}'."
            )

        # load data from local sources first
        local_data: typing.List[plugin_data.LocalData] = []
        for named_plugin in named_plugins:
            plugin_update_result = named_plugin.entry_instance.update(args)
            for local_data_item in plugin_update_result.local_data:
                local_data_item.data = list(local_data_item.load_resources())
            local_data.extend(plugin_update_result.local_data)

        logger.info("Loaded %s local data sources.", len(local_data))

        # allow running multiple plugins at once
        # gather WebData subclasses and run the spider
        web_data: typing.List[plugin_data.WebData] = []
        for named_plugin in named_plugins:
            plugin_update_result = named_plugin.entry_instance.update(args)
            web_data.extend(plugin_update_result.web_data)

        logger.info("Starting %s web data sources.", len(web_data))

        # run the web data to get items, using scrapy
        # save the feed to a temp file, then read the items back in
        feed_items = []
        with tempfile.TemporaryDirectory() as temp_dir:
            feed_path = pathlib.Path(temp_dir, "feed_%(name)s_%(time)s.pickle")
            feed_path_setting = str(feed_path).replace("\\", "/")

            process = CrawlerProcess(
                settings={
                    "HTTPCACHE_ENABLED": True,
                    "HTTPCACHE_DIR": ".httpcache",
                    "HTTPCACHE_POLICY": "scrapy.extensions.httpcache.RFC2616Policy",
                    "EXTENSIONS": {
                        "scrapy.extensions.telnet.TelnetConsole": None,
                    },
                    "FEED_EXPORTERS": {
                        "pickle_raw": "gather_vision.app.AppPickleItemExporter",
                    },
                    "FEEDS": {
                        f"file:///{feed_path_setting}": {"format": "pickle_raw"},
                    },
                    "WEB_DATA_ITEMS": web_data,
                    "LOG_ENABLED": True,
                    "LOG_FILE": None,
                    "LOG_STDOUT": False,
                    "LOG_LEVEL": "ERROR",
                },
                install_root_handler=True,
            )

            process.crawl(WebDataFetch)

            logging.getLogger("scrapy").setLevel("ERROR")
            logging.getLogger("py.warnings").setLevel("CRITICAL")

            # the script will block here until the crawling is finished
            process.start()

            # f = io.BytesIO()
            # pickle.dump(items, f)
            #
            # f.seek(0)
            # result = pickle.load(f)

            # load the feed items
            for item in feed_path.parent.iterdir():
                if not item.is_file():
                    continue
                if item.suffix != ".pickle":
                    continue

                with item.open("rb") as f:
                    while True:
                        try:
                            feed_items.append(pickle.load(f))
                        except EOFError:
                            break

        logger.info("Loaded %s data items from web data sources.", len(feed_items))
        logger.info("Finished update.")

        return plugin_entry.UpdateResult(web_data=web_data, local_data=local_data)

    def list(self, args: plugin_entry.ListArgs) -> plugin_entry.ListResult:
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
        return plugin_entry.ListResult(items)

    def _get_entry_points(self, group: str):
        return entry_points(group=group)

    def _build_plugin_item(self, entry_point: EntryPoint) -> PluginItem:
        entry_class = entry_point.load()
        item = PluginItem(
            entry_point=entry_point,
            entry_class=entry_class,
            entry_instance=entry_class(),
        )
        return item


class WebDataFetch(scrapy.Spider):
    name = "web-data"

    def start_requests(self):
        web_data_items: typing.List[plugin_data.WebData] = self.settings.get(
            "WEB_DATA_ITEMS"
        )
        for web_data_item in web_data_items:
            for initial_url in web_data_item.initial_urls():
                yield scrapy.Request(
                    url=initial_url,
                    callback=self.parse,
                    meta={"web_data_item": web_data_item},
                )

    def parse(self, response: Response, **kwargs):
        web_data_item: plugin_data.WebData = response.meta["web_data_item"]

        is_json = "json" in response.headers["Content-Type"].decode("utf-8").lower()

        if isinstance(response, TextResponse):
            body_data = response.json() if is_json else None
            selector = response.selector
        else:
            body_data = None
            selector = None

        data = plugin_data.WebDataAvailable(
            request_url=response.request.url,
            request_method=response.request.method,
            response_url=response.url,
            body_text=response.text,
            body_data=body_data,
            selector=selector,
            status=response.status,
            headers=response.headers,
            meta=response.meta,
        )
        for i in web_data_item.parse_response(data):
            if isinstance(i, str):
                yield scrapy.Request(
                    url=i, callback=self.parse, meta={"web_data_item": web_data_item}
                )
            else:
                yield i
