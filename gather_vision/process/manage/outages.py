from pathlib import Path
from zoneinfo import ZoneInfo

import gather_vision.models as app_models
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.service.outages.energex_events import EnergexEvents
from gather_vision.process.service.outages.energex_import import EnergexImport


class Outages:
    def __init__(self, logger: Logger, tz: ZoneInfo, http_client: HttpClient):
        normalise = Normalise()

        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._tz = tz

    def run_update(self):
        self.create_energex()
        ee = EnergexEvents(
            self._logger,
            self._http_client,
            self._normalise,
            self._tz,
        )
        ee.update_outages()

    def run_import(self, path: Path):
        self.create_energex()
        ei = EnergexImport(
            self._logger,
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
