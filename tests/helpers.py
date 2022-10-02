import logging

from gather_vision import model
from gather_vision.plugin import Entry

logger = logging.getLogger(__name__)


class ExamplePlugin(Entry):
    plugin_name = "example-plugin"
    plugin_value = "helpers.ExamplePlugin"
    _data_source_names = ["example-data-source-1", "example-data-source-2"]

    def update(self, args: model.UpdateArgs) -> model.UpdateResult:
        logger.info(f"Running update for plugin {self.plugin_name}.")
        return model.UpdateResult()

    def list(self, args: model.ListArgs) -> model.ListResult:
        logger.info(f"Running list for plugin {self.plugin_name}.")
        return model.ListResult(items={self.plugin_name: self._data_source_names})
