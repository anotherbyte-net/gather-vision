from pathlib import Path

import pytz

from gather_vision.process.component.html_extract import HtmlExtract
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.service.energex_events import EnergexEvents
import gather_vision.models as app_models
from gather_vision.process.service.energex_import import EnergexImport


class Outages:
    def __init__(self, logger: Logger, tz: pytz.timezone):
        http_client = HttpClient(logger, use_cache=True)
        normalise = Normalise()
        html_extract = HtmlExtract()

        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._html_extract = html_extract
        self._tz = tz

    def update_outages(self):
        self.create_energex()
        ee = EnergexEvents(
            self._logger,
            self._http_client,
            self._normalise,
            self._html_extract,
            self._tz,
        )
        ee.update_outages()

    def import_outages(self, path: Path):
        self.create_energex()
        ei = EnergexImport(
            self._logger,
            self._http_client,
            self._normalise,
            self._tz,
        )
        ei.import_outages(path)

    def create_energex(self):
        obj, created = app_models.InformationSource.objects.get_or_create(
            name=EnergexEvents.code,
            defaults={
                "title": "Energex",
                "info_url": "https://www.energex.com.au",
            },
        )
        return obj, created
