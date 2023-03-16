import sys

import pytest
import importlib_metadata

import example_plugin
from gather_vision import app, cli

expected_version = "0.0.4"

if sys.version_info.minor >= 10:
    help_phrase_options = "options:"
else:
    help_phrase_options = "optional arguments:"


@pytest.mark.parametrize("main_args,exit_code", [([], 1), (["--help"], 0)])
def test_cli_no_args(capsys, caplog, main_args, exit_code, equal_ignore_whitespace):
    with pytest.raises(SystemExit, match=str(exit_code)):
        cli.main(main_args)

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
        equal_ignore_whitespace(stdout, prog_help)
        assert stderr == ""
        assert caplog.record_tuples == []

    if main_args == []:
        assert stdout == ""
        equal_ignore_whitespace(stderr, prog_help)
        assert caplog.record_tuples == []


def test_cli_version(capsys, caplog):
    with pytest.raises(SystemExit, match="0"):
        cli.main(["--version"])

    stdout, stderr = capsys.readouterr()
    assert stdout == f"gather-vision {expected_version}\n"
    assert stderr == ""
    assert caplog.record_tuples == []


def test_cli_list_help(capsys, caplog, equal_ignore_whitespace):
    with pytest.raises(SystemExit, match="0"):
        cli.main(["list", "--help"])

    stdout, stderr = capsys.readouterr()
    equal_ignore_whitespace(
        stdout,
        (
            "usage: gather-vision list [-h] "
            f"{help_phrase_options} "
            "  -h, --help  show this help message and exit"
        ),
    )
    assert stderr == ""
    assert caplog.record_tuples == []


def test_cli_list(capsys, caplog, monkeypatch):

    with monkeypatch.context() as m:
        from gather_vision.app import App

        orig_build_plugin_item = App._build_plugin_item

        def get_entry_points(self, group):
            result = importlib_metadata.EntryPoints(
                [i for i in importlib_metadata.entry_points(group=group)]
                + [
                    importlib_metadata.EntryPoint(
                        group=App.group,
                        name=example_plugin.ExamplePlugin.plugin_name,
                        value=example_plugin.ExamplePlugin.plugin_value,
                    )
                ]
            )
            return result

        def build_plugin_item(self, entry_point):
            if entry_point.name == example_plugin.ExamplePlugin.plugin_name:
                return app.PluginItem(
                    entry_point=entry_point,
                    entry_class=example_plugin.ExamplePlugin,
                    entry_instance=example_plugin.ExamplePlugin(),
                )
            return orig_build_plugin_item(self, entry_point)

        m.setattr(App, "_get_entry_points", get_entry_points)

        m.setattr(App, "_build_plugin_item", build_plugin_item)

        with pytest.raises(SystemExit, match="0"):
            cli.main(["list"])

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""
    assert caplog.record_tuples == [
        ("gather_vision.cli", 20, "Starting gather-vision."),
        ("gather_vision.app", 20, "Loaded 1 plugins."),
        ("example_plugin", 20, "Running list for plugin example-plugin."),
        ("gather_vision.cli", 20, "Listing 1 plugins."),
        ("gather_vision.cli", 20, "  1) example-plugin"),
        ("gather_vision.cli", 20, "    1.1) example-data-source-1"),
        ("gather_vision.cli", 20, "    1.2) example-data-source-2"),
        ("gather_vision.cli", 20, "Finished."),
    ]


def test_cli_update_help(capsys, caplog, equal_ignore_whitespace):
    with pytest.raises(SystemExit, match="0"):
        cli.main(["--log-level", "debug", "update", "--help"])

    stdout, stderr = capsys.readouterr()

    equal_ignore_whitespace(
        stdout,
        (
            "usage: gather-vision update [-h] [--name NAME] [--data-path DATA_PATH]\n"
            "\n"
            f"{help_phrase_options}\n"
            "  -h, --help            show this help message and exit\n"
            "  --name NAME           The name of the update to run.\n"
            "  --data-path DATA_PATH\n"
            "                        The path to the data directory for downloads, cache, files.\n"
        ),
    )
    assert stderr == ""
    assert caplog.record_tuples == []


def test_cli_update_not_available(capsys, caplog):
    with pytest.raises(SystemExit, match="1"):
        cli.main(["update", "--name", "not-available"])

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""
    assert caplog.record_tuples == [
        ("gather_vision.cli", 20, "Starting gather-vision."),
        ("gather_vision.cli", 20, "Updating 'not-available'."),
        (
            "gather_vision.cli",
            40,
            "Error: GatherVisionException - Could not find plugin named 'not-available'. "
            "Available plugins (1): example-plugin.",
        ),
    ]


def test_cli_update_example_plugin(capsys, caplog, tmp_path):
    with pytest.raises(SystemExit, match="0"):
        cli.main(["update", "--name", "example-plugin", "--data-path", str(tmp_path)])

    # logging_tree_str = logging_tree.format.build_description()

    l_cli = "gather_vision.cli"
    l_app = "gather_vision.app"

    prefix = "  1) plugin 'example-plugin' data source 'example-data-source-"

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""
    for index, log_item in [
        (0, (l_cli, 20, "Starting gather-vision.")),
        (1, (l_cli, 20, "Updating 'example-plugin'.")),
        (2, ("example_plugin", 20, "Running update for plugin example-plugin.")),
        (3, (l_app, 20, "Loaded 1 local data sources.")),
        (4, (l_app, 20, "Starting 1 web data sources.")),
        (18, (l_app, 20, "Loaded 2 data items from web data sources.")),
        (19, (l_app, 20, "Finished update.")),
        (20, (l_cli, 20, "Updated 1 local data items.")),
        (21, (l_cli, 20, prefix + "2' with 2 items")),
        (22, (l_cli, 20, "Updated 1 web data items.")),
        (23, (l_cli, 20, prefix + "1' with 2 items")),
        (24, (l_cli, 20, "Finished.")),
    ]:
        assert caplog.record_tuples[index] == log_item
