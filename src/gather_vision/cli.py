"""Command line for gather vision."""

import argparse
import logging
import sys
import typing

from gather_vision import app, model, utils


def cli_update(args: argparse.Namespace) -> bool:
    """Run the update action from the cli.

    Args:
        args: The arguments for the update action.

    Returns:
        True if there were no errors.
    """
    logger = logging.getLogger(__name__)

    app_args = model.UpdateArgs(name=args.name)
    main_app = app.App()

    logger.info("Updating '%s'.", args.name)
    main_app.update(app_args)
    return True


def cli_show(args: argparse.Namespace) -> bool:
    """Run the show action from the cli.

    Args:
        args: The arguments for the show action.

    Returns:
        True if there were no errors.
    """
    logger = logging.getLogger(__name__)

    app_args = model.ShowArgs(name=args.name)
    main_app = app.App()

    logger.info("Showing '%s'.", args.name)
    main_app.show(app_args)
    return True


def cli_list(
    args: argparse.Namespace,  # noqa: U100 pylint: disable=unused-argument
) -> bool:
    """Run the list action from the cli.

    Args:
        args: The arguments for the list action.

    Returns:
        True if there were no errors.
    """
    logger = logging.getLogger(__name__)

    app_args = model.ListArgs()
    main_app = app.App()
    result = main_app.list(app_args)

    logger.info("Listing %s plugins.", len(result.names))
    for index, name in enumerate(result.names):
        logger.info("  %s) %s", index + 1, name)
    return True


def main(args: typing.Optional[typing.List[str]] = None) -> int:
    """Run as a command line program.

    Args:
        args: The program arguments.

    Returns:
        int: Program exit code.
    """
    if args is None:
        args = sys.argv[1:]

    # configure logging
    logging.basicConfig(
        format="%(asctime)s [%(levelname)-8s] %(message)s", level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)

    # create the top-level parser
    parser = argparse.ArgumentParser(
        prog=utils.get_name_dash(),
        description="Obtain, extract, organise, and store information.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {utils.get_version()}",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="The log level: 'debug', 'info', 'warning', 'error', 'critical'.",
    )
    subparsers = parser.add_subparsers(
        title="Available subcommands",
        description="The actions available for plugins",
        dest="subcommand_action",
        required=False,
        help="The subcommands available to interact with "
        "installed plugins ('list', 'update', 'show').",
        metavar="action",
    )

    # create the parser for the "update" command
    parser_update = subparsers.add_parser("update")
    parser_update.add_argument(
        "name",
        help="The name of the update to run.",
    )
    parser_update.set_defaults(func=cli_update)

    # create the parser for the "show" command
    parser_show = subparsers.add_parser("show")
    parser_show.add_argument(
        "name",
        help="The name of the group of information to show.",
    )
    parser_show.set_defaults(func=cli_show)

    # create the parser for the "list" command
    parser_list = subparsers.add_parser("list")
    parser_list.set_defaults(func=cli_list)

    try:
        parsed_args = parser.parse_args(args)

        logging.getLogger().setLevel((parsed_args.log_level or "info").upper())

        if not parsed_args.subcommand_action:
            parser.print_help(file=sys.stderr)
            sys.exit(1)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Starting %s with arguments '%s'.", utils.get_name_dash(), args
            )
        else:
            logger.info("Starting %s.", utils.get_name_dash())

        if parsed_args.subcommand_action and hasattr(parsed_args, "func"):
            result = parsed_args.func(parsed_args)
        else:
            logger.warning("Not sure what to do with arguments '%s'.", args)
            result = False

        outcome = 0 if result is True else 1
        if outcome == 0:
            logger.info("Finished.")
        else:
            logger.info("Finished with exit code %s.", outcome)

        return sys.exit(outcome)

    except utils.GatherVisionException as error:
        if logger.isEnabledFor(logging.DEBUG):
            raise
        logger.error("Error: %s - %s", error.__class__.__name__, str(error))
        return sys.exit(1)

    except Exception as error:  # pylint: disable=broad-except
        if logger.isEnabledFor(logging.DEBUG):
            raise
        logger.error("Error: %s - %s", error.__class__.__name__, str(error))
        return sys.exit(2)


if __name__ == "__main__":
    main()
