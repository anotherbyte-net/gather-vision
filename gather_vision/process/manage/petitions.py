from pathlib import Path
from zoneinfo import ZoneInfo

from gather_vision import models as app_models
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.service.petition.au_qld import AuQld
from gather_vision.process.service.petition.au_qld_bcc import AuQldBcc
from gather_vision.process.service.petition.petition_import import PetitionImport


class Petitions:
    def __init__(self, logger: Logger, tz: ZoneInfo, http_client: HttpClient):
        normalise = Normalise()
        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._tz = tz

    def run_update(self) -> None:
        self.create_au_qld()
        pu_au_qld = AuQld(
            self._logger,
            self._http_client,
            self._normalise,
            self._tz,
        )
        pu_au_qld.update_petitions()

        self.create_au_qld_bcc()
        pu_au_qld_bcc = AuQldBcc(
            self._logger,
            self._http_client,
            self._normalise,
            self._tz,
        )
        pu_au_qld_bcc.update_petitions()

    def run_import(self, path: Path) -> None:
        self.create_au_qld()
        self.create_au_qld_bcc()
        pi = PetitionImport(self._logger, self._normalise, self._tz)
        pi.import_petitions(path)

    def create_au_qld(self):
        url = "https://www.parliament.qld.gov.au/Work-of-the-Assembly/Petitions"
        obj, created = app_models.InformationSource.objects.get_or_create(
            name=AuQld.code,
            defaults={
                "title": "Queensland Government Petitions",
                "info_url": url,
            },
        )
        return obj, created

    def create_au_qld_bcc(self):
        obj, created = app_models.InformationSource.objects.get_or_create(
            name=AuQldBcc.code,
            defaults={
                "title": "Brisbane City Council Petitions",
                "info_url": "https://www.epetitions.brisbane.qld.gov.au/",
            },
        )
        return obj, created
