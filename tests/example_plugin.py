import dataclasses
import logging
import typing


logger = logging.getLogger(__name__)

logging.getLogger("example_plugin").setLevel("INFO")


class ExamplePlugin(entry.Entry):
    plugin_name = "example-plugin"
    plugin_value = "example_plugin.ExamplePlugin"
    _data_source_1 = "example-data-source-1"
    _data_source_2 = "example-data-source-2"
    _data_source_names = [_data_source_1, _data_source_2]

    def update(self, args: entry.UpdateArgs) -> entry.UpdateResult:
        logger.info(f"Running update for plugin {self.plugin_name}.")
        return entry.UpdateResult(
            web_data=[
                ExamplePluginWebData(
                    plugin_name=self.plugin_name,
                    plugin_data_source=self._data_source_1,
                )
            ],
            local_data=[
                ExamplePluginLocalData(
                    plugin_name=self.plugin_name,
                    plugin_data_source=self._data_source_2,
                )
            ],
        )

    def list(self, args: entry.ListArgs) -> entry.ListResult:
        logger.info(f"Running list for plugin {self.plugin_name}.")
        return entry.ListResult(
            items={self.plugin_name: self._data_source_names},
        )


class ExamplePluginWebData(data.WebData):
    def initial_urls(self) -> typing.Iterable[str]:
        return ["https://example.com/"]

    def parse_response(
        self, data: data.WebDataAvailable
    ) -> typing.Generator[
        typing.Union[str, data.GatherDataItem], typing.Any, typing.Any
    ]:
        yield ExamplePluginDataItem(
            plugin_name=self.plugin_name,
            plugin_data_source=self.plugin_data_source,
            name="three",
            value=3,
        )
        yield ExamplePluginDataItem(
            plugin_name=self.plugin_name,
            plugin_data_source=self.plugin_data_source,
            name="four",
            value=4,
        )


@dataclasses.dataclass
class ExamplePluginDataItem(data.GatherDataItem):
    name: str
    value: int


class ExamplePluginLocalData(data.LocalData):
    def load_resources(
        self,
    ) -> typing.Generator[data.GatherDataItem, typing.Any, typing.Any]:
        items = [
            ExamplePluginDataItem(
                plugin_name=self.plugin_name,
                plugin_data_source=self.plugin_data_source,
                name="one",
                value=1,
            ),
            ExamplePluginDataItem(
                plugin_name=self.plugin_name,
                plugin_data_source=self.plugin_data_source,
                name="two",
                value=2,
            ),
        ]

        for item in items:
            yield item
