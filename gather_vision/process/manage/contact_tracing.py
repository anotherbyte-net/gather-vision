from zoneinfo import ZoneInfo

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger


class ContactTracing:
    def __init__(self, logger: Logger, tz: ZoneInfo, http_client: HttpClient):
        self._logger = logger
        self._http_client = http_client
        self._tz = tz

    def run_update(self):
        pass
