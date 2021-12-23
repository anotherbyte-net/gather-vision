import contextlib
from collections import namedtuple
from typing import Iterable, Optional
from unittest import mock


def example_data_dir():
    from importlib import resources

    with resources.path("gather_vision_proj", "settings.py") as p:
        return p.resolve().parent.parent / ".local" / "example_data"


@contextlib.contextmanager
def mock_http_client_send_request(set_side_effect):
    with mock.patch(
        "gather_vision.management.commands.visionprocess.HttpClient._send_request",
        spec=True,
        spec_set=True,
    ) as http_request:
        http_request.side_effect = set_side_effect
        try:
            yield http_request
        finally:
            pass


def match_output(
    context,
    actual: str,
    expected: list[tuple[str, str]],
    start: Optional[int] = None,
    stop: Optional[int] = None,
):
    actual = actual.strip() if actual else ""
    actual = actual.split("\n")
    actual = [i.strip() for i in actual if i and i.strip()]

    if start is None:
        start = 0
    if stop is None:
        stop = len(actual)
    actual = actual[start:stop]

    if len(actual) != len(expected):
        context.fail(
            f"Actual has {len(actual)} entries, expected has {len(expected)}: {actual}; {expected}"
        )

    for index, (act_line, (exp_lvl, exp_line)) in enumerate(zip(actual, expected)):
        act_date, act_rest = act_line.split(" ", maxsplit=1)

        exp_lvl_str = f"[{exp_lvl:8}] "
        context.assertTrue(
            act_rest.startswith(exp_lvl_str),
            f"Actual did not match expected log level '{exp_lvl_str}'.",
        )

        exp_rest = f"{exp_lvl_str}{exp_line}"
        context.assertEqual(
            exp_rest,
            act_rest,
            f"Actual did not match expected '{act_rest}' != '{exp_rest}'.",
        )


RequestsTestResponse = namedtuple(
    "RequestsTestResponse",
    ["text", "json", "content"],
    defaults=[None, None, None],
)
