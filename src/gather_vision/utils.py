"""Small utility functions."""
import pathlib
import typing

from importlib_metadata import PackageNotFoundError, distribution
from importlib_resources import as_file, files


def get_name_dash() -> str:
    """Get the package name with word separated by dashes."""
    return "gather-vision"


def get_name_under() -> str:
    """Get the package name with word separated by underscores."""
    return "gather_vision"


def get_version() -> typing.Optional[str]:
    """Get the package version."""
    try:
        dist = distribution(get_name_dash())
        return dist.version
    except PackageNotFoundError:
        pass

    try:
        with as_file(files(get_name_under()).joinpath("cli.py")) as file_path:
            return (file_path.parent.parent.parent / "VERSION").read_text().strip()
    except FileNotFoundError:
        pass

    return None


def validate(name: str, value, expected: typing.List) -> None:
    """Validate that a value is one of the expected values."""
    if value is not None and value not in expected:
        opts = ", ".join(sorted([str(i) for i in expected]))
        raise GatherVisionException(
            f"Invalid {name} '{value}'. Expected one of '{opts}'."
        )


def validate_path(
    name: str, value: pathlib.Path, must_exist: bool = False
) -> pathlib.Path:
    """Validate a path."""
    if not value:
        raise GatherVisionException(f"Must provide path {name}.")

    try:
        if must_exist is True:
            abs_path = value.resolve(strict=True)
        else:
            abs_path = value.absolute()

        return abs_path
    except Exception as error:
        raise GatherVisionException(f"Invalid path '{value}'.") from error


class GatherVisionException(Exception):
    """A gather vision error."""
