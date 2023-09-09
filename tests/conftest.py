import re

import importlib_metadata

import pytest

import example_plugin


@pytest.fixture(autouse=True)
def patch_app_get_entry_points(monkeypatch):
    """Provide an example plugin for tests."""

    def _get_entry_points(self, group: str):
        return importlib_metadata.EntryPoints(example_plugin.ExamplePlugin)

    monkeypatch.setattr("gather_vision.app.App._get_entry_points", _get_entry_points)


@pytest.fixture()
def equal_ignore_whitespace():
    def _equal_ignore_whitespace(value1: str, value2: str, ignore_case=False):
        # Ignore non-space and non-word characters
        whitespace = re.compile(r"\s+")
        replace1 = whitespace.sub(" ", value1 or "").strip()
        replace2 = whitespace.sub(" ", value2 or "").strip()

        if ignore_case:
            assert replace1.casefold() == replace2.casefold()
        else:
            assert replace1 == replace2

    return _equal_ignore_whitespace
