import logging
from typing import Optional


class Logger:
    def __init__(
        self, logger: Optional[logging.Logger] = None, stdout=None, style=None
    ):
        if logger and (stdout or style):
            raise ValueError(
                "Must specify at most one of logger and (stdout or style)."
            )

        if (stdout and not style) or (not stdout and style):
            raise ValueError("Must both stdout and style.")

        if not logger and not stdout and not style:
            logger = logging.getLogger()

        self._stdout = stdout
        self._style = style
        self._logger = logger

    def debug(self, message: str):
        if self._stdout:
            self._stdout.write(self._style.NOTICE(message))
        else:
            self._logger.debug(message)

    def info(self, message: str):
        if self._stdout:
            self._stdout.write(self._style.SUCCESS(message))
        else:
            self._logger.info(message)

    def warning(self, message: str):
        if self._stdout:
            self._stdout.write(self._style.WARNING(message))
        else:
            self._logger.warning(message)

    def error(self, message: str):
        if self._stdout:
            self._stdout.write(self._style.ERROR(message))
        else:
            self._logger.error(message)
