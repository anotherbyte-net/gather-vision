import sys
from importlib_metadata import EntryPoints, entry_points, EntryPoint

import pytest

from gather_vision.app import PluginItem
from gather_vision.cli import main
from helpers import ExamplePlugin, collapse_whitespace

expected_version = "0.0.3"

if sys.version_info.minor >= 10:
    help_phrase_options = "options:"
else:
    help_phrase_options = "optional arguments:"


@pytest.mark.parametrize("main_args,exit_code", [([], 1), (["--help"], 0)])
def test_cli_no_args(capsys, caplog, main_args, exit_code):
    with pytest.raises(SystemExit, match=str(exit_code)):
        main(main_args)

    prog_help = (
        "usage: gather-vision [-h] [--version]\n"
        "                     [--log-level {debug,info,warning,error,critical}]\n"
        "                     action ...\n"
        "\n"
        "Obtain, extract, organise, and store information.\n"
        "\n"
        f"{help_phrase_options}\n"
        "  -h, --help            show this help message and exit\n"
        "  --version             show program's version number and exit\n"
        "  --log-level {debug,info,warning,error,critical}\n"
        "                        The log level: 'debug', 'info', 'warning', 'error',\n"
        "                        'critical'.\n"
        "\n"
        "Available subcommands:\n"
        "  The actions available for plugins\n"
        "\n"
        "  action                The subcommands available to interact with "
        "installed\n"
        "                        plugins ('list', 'update').\n"
    )

    stdout, stderr = capsys.readouterr()
    if main_args == ["--help"]:
        assert collapse_whitespace(stdout) == collapse_whitespace(prog_help)
        assert stderr == ""
        assert caplog.record_tuples == []

    if main_args == []:
        assert stdout == ""
        assert collapse_whitespace(stderr) == collapse_whitespace(prog_help)
        assert caplog.record_tuples == []


def test_cli_version(capsys, caplog):
    with pytest.raises(SystemExit, match="0"):
        main(["--version"])

    stdout, stderr = capsys.readouterr()
    assert stdout == f"gather-vision {expected_version}\n"
    assert stderr == ""
    assert caplog.record_tuples == []


def test_cli_list_help(capsys, caplog):
    with pytest.raises(SystemExit, match="0"):
        main(["list", "--help"])

    stdout, stderr = capsys.readouterr()
    assert stdout == (
        "usage: gather-vision list [-h]\n"
        "\n"
        f"{help_phrase_options}\n"
        "  -h, --help  show this help message and exit\n"
    )
    assert stderr == ""
    assert caplog.record_tuples == []


def test_cli_list(capsys, caplog, monkeypatch):

    with monkeypatch.context() as m:
        from gather_vision.app import App

        orig_build_plugin_item = App._build_plugin_item

        def get_entry_points(self, group):
            result = EntryPoints(
                [i for i in entry_points(group=group)]
                + [
                    EntryPoint(
                        group=App.group,
                        name=ExamplePlugin.plugin_name,
                        value=ExamplePlugin.plugin_value,
                    )
                ]
            )
            return result

        def build_plugin_item(self, entry_point):
            if entry_point.name == ExamplePlugin.plugin_name:
                return PluginItem(
                    entry_point=entry_point,
                    entry_class=ExamplePlugin,
                    entry_instance=ExamplePlugin(),
                )
            return orig_build_plugin_item(self, entry_point)

        m.setattr(App, "_get_entry_points", get_entry_points)

        m.setattr(App, "_build_plugin_item", build_plugin_item)

        with pytest.raises(SystemExit, match="0"):
            main(["list"])

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""
    assert caplog.record_tuples == [
        ("gather_vision.cli", 20, "Starting gather-vision."),
        ("gather_vision.app", 20, "Loaded 1 plugins."),
        ("helpers", 20, "Running list for plugin example-plugin."),
        ("gather_vision.cli", 20, "Listing 1 plugins."),
        ("gather_vision.cli", 20, "  1) example-plugin"),
        ("gather_vision.cli", 20, "    1.1) example-data-source-1"),
        ("gather_vision.cli", 20, "    1.2) example-data-source-2"),
        ("gather_vision.cli", 20, "Finished."),
    ]


def test_cli_update_help(capsys, caplog):
    with pytest.raises(SystemExit, match="0"):
        main(["--log-level", "debug", "update", "--help"])

    stdout, stderr = capsys.readouterr()
    assert stdout == (
        "usage: gather-vision update [-h] [--name NAME]\n"
        "\n"
        f"{help_phrase_options}\n"
        "  -h, --help   show this help message and exit\n"
        "  --name NAME  The name of the update to run.\n"
    )
    assert stderr == ""
    assert caplog.record_tuples == []


def test_cli_update_not_available(capsys, caplog):
    with pytest.raises(SystemExit, match="1"):
        main(["update", "--name", "not-available"])

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""
    assert caplog.record_tuples == [
        ("gather_vision.cli", 20, "Starting gather-vision."),
        ("gather_vision.cli", 20, "Updating 'not-available'."),
        (
            "gather_vision.cli",
            40,
            "Error: GatherVisionException - Could not find plugin named 'not-available'.",
        ),
    ]


def test_cli_update_example_plugin(capsys, caplog):
    with pytest.raises(SystemExit, match="0"):
        main(["update", "--name", "example-plugin"])

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""
    assert caplog.record_tuples == [
        ("gather_vision.cli", 20, "Starting gather-vision."),
        ("gather_vision.cli", 20, "Updating 'example-plugin'."),
        ("helpers", 20, "Running update for plugin example-plugin."),
        ("gather_vision.app", 20, "Loaded 1 local data sources."),
        ("helpers", 20, "Running update for plugin example-plugin."),
        ("gather_vision.app", 20, "Starting 1 web data sources."),
        ("gather_vision.app", 20, "Loaded 2 data items from web data sources."),
        ("gather_vision.app", 20, "Finished update."),
        ("gather_vision.cli", 20, "Finished."),
    ]
