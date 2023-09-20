import re
import pytest
import logging

logging.basicConfig(
    format="%(asctime)s [%(levelname)-8s] %(message)s", level=logging.DEBUG
)


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
