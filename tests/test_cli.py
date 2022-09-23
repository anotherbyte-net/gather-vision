import pytest

from gather_vision.cli import main


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
        "options:\n"
        "  -h, --help            show this help message and exit\n"
        "  --version             show program's version number and exit\n"
        "  --log-level {debug,info,warning,error,critical}\n"
        "                        the log level: debug, info, warning, error, "
        "critical\n"
        "\n"
        "Available subcommands:\n"
        "  The actions available for plugins\n"
        "\n"
        "  action                The subcommands available to interact with "
        "installed\n"
        "                        plugins.\n"
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


def test_cli_show_not_available(capsys, caplog):
    with pytest.raises(SystemExit, match="1"):
        main(["show", "not-available"])

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""
    assert caplog.record_tuples == [
        ("gather_vision.cli", 20, "Starting gather-vision."),
        ("gather_vision.cli", 20, "Showing 'not-available'."),
        (
            "gather_vision.cli",
            40,
            "Error: GatherVisionException - Could not find plugin named 'not-available'.",
        ),
    ]


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
