import sys

import pytest

from gather_vision.cli import main

expected_version = "0.0.1"

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
        assert stdout == prog_help
        assert stderr == ""
        assert caplog.record_tuples == []

    if main_args == []:
        assert stdout == ""
        assert stderr == prog_help
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


def test_cli_list(capsys, caplog):
    with pytest.raises(SystemExit, match="0"):
        main(["list"])

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""
    assert caplog.record_tuples == [
        ("gather_vision.cli", 20, "Starting gather-vision."),
        ("gather_vision.cli", 20, "Listing 0 plugins."),
        ("gather_vision.cli", 20, "Finished."),
    ]


def test_cli_update_help(capsys, caplog):
    with pytest.raises(SystemExit, match="0"):
        main(["update", "--help"])

    stdout, stderr = capsys.readouterr()
    assert stdout == (
        "usage: gather-vision update [-h] name\n"
        "\n"
        "positional arguments:\n"
        "  name        The name of the update to run.\n"
        "\n"
        f"{help_phrase_options}\n"
        "  -h, --help  show this help message and exit\n"
    )
    assert stderr == ""
    assert caplog.record_tuples == []


def test_cli_update_not_available(capsys, caplog):
    with pytest.raises(SystemExit, match="1"):
        main(["update", "not-available"])

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
