from pathlib import Path

import pytz

from gather_vision.process.component.html_extract import HtmlExtract
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.service.petition_import import PetitionImport
from gather_vision.process.service.petitions_au_qld import PetitionsAuQld
from gather_vision.process.service.petitions_au_qld_bcc import PetitionsAuQldBcc
from gather_vision import models as app_models


class Petitions:
    def __init__(self, logger: Logger, tz: pytz.timezone):
        http_client = HttpClient(logger, use_cache=True)
        normalise = Normalise()
        html_extract = HtmlExtract()
        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._html_extract = html_extract
        self._tz = tz

    def update_petitions(self) -> None:
        self.create_au_qld()
        pu_au_qld = PetitionsAuQld(
            self._logger,
            self._http_client,
            self._normalise,
            self._html_extract,
            self._tz,
        )
        pu_au_qld.update_petitions()

        self.create_au_qld_bcc()
        pu_au_qld_bcc = PetitionsAuQldBcc(
            self._logger,
            self._http_client,
            self._normalise,
            self._html_extract,
            self._tz,
        )
        pu_au_qld_bcc.update_petitions()

    def import_petitions(self, path: Path) -> None:
        self.create_au_qld()
        self.create_au_qld_bcc()
        pi = PetitionImport(
            self._logger,
            self._http_client,
            self._normalise,
            self._html_extract,
            self._tz,
        )
        pi.import_petitions(path)

    def create_au_qld(self):
        url = "https://www.parliament.qld.gov.au/Work-of-the-Assembly/Petitions"
        obj, created = app_models.InformationSource.objects.get_or_create(
            name=PetitionsAuQld.code,
            defaults={
                "title": "Queensland Government Petitions",
                "info_url": url,
            },
        )
        return obj, created

    def create_au_qld_bcc(self):
        obj, created = app_models.InformationSource.objects.get_or_create(
            name=PetitionsAuQldBcc.code,
            defaults={
                "title": "Brisbane City Council Petitions",
                "info_url": "https://www.epetitions.brisbane.qld.gov.au/",
            },
        )
        return obj, created
