from importlib_metadata import EntryPoints

import pytest

from example_plugin import ExamplePlugin


@pytest.fixture(autouse=True)
def patch_app_get_entry_points(monkeypatch):
    """Provide an example plugin for tests."""

    def _get_entry_points(self, group: str):
        return EntryPoints(ExamplePlugin)

    monkeypatch.setattr("gather_vision.app.App._get_entry_points", _get_entry_points)
