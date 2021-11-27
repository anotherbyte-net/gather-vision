from pathlib import Path

import pytz

from gather_vision.models import PetitionSource, PetitionItem, PetitionChange
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.component.sqlite_client import SqliteClient


class Petitions:
    def __init__(self, logger: Logger, tz: pytz.timezone):
        http_client = HttpClient(logger, use_cache=True)
        normalise = Normalise()

        self._logger = logger
        self._tz = tz

        self._http_client = http_client
        self._normalise = normalise

        self._source_au_qld = None
        self._source_au_qld_bcc = None

    def update_petitions(self):
        self.create_sources()
        raise NotImplementedError()

    def import_petitions(self, path: Path):
        self.create_sources()

        db = SqliteClient(path)
        conn = db.get_sqlite_db()
        table_names = list(db.get_table_names(conn))
        for table_name in table_names:
            for row in db.get_table_data(conn, table_name):
                row_keys = list(row.keys())
                row_values = list(row)
                row_data = dict(zip(row_keys, row_values))
                self.import_row(row_data)

    def import_row(self, data: dict):
        if self.is_au_qld(data):
            return self.import_au_qld(data)
        elif self._is_au_qld_bcc(data):
            return self.import_au_qld_bcc(data)

        raise ValueError()

    def import_au_qld(self, data: dict):
        source = self._source_au_qld
        title = self._normalise.petition_text(data.get("subject"))
        code = data.get("reference_num")
        view_url = data.get("url")
        principal = self._normalise.petition_text(data.get("principal"))
        body = data.get("body")
        opened_date = self._normalise.parse_date(data.get("posted_at"), self._tz)
        closed_date = self._normalise.parse_date(data.get("closed_at"), self._tz)
        eligibility = self._normalise.petition_text(data.get("eligibility"))
        sponsor = self._normalise.petition_text(data.get("sponsor"))

        retrieved_date = self._normalise.parse_date(data.get("retrieved_at"), self._tz)
        signatures = str(data.get("signatures", ""))
        signatures = int(signatures, 10) if signatures else 0

        petition, petition_created = PetitionItem.objects.get_or_create(
            source=source,
            code=code,
            defaults={
                "title": title,
                "view_url": view_url,
                "principal": principal,
                "body": body,
                "opened_date": opened_date,
                "closed_date": closed_date,
                "eligibility": eligibility,
                "sponsor": sponsor,
            },
        )

        change, change_created = PetitionChange.objects.get_or_create(
            petition=petition,
            retrieved_date=retrieved_date,
            defaults={"signatures": signatures},
        )

        return petition, change

    def import_au_qld_bcc(self, data: dict):
        source = self._source_au_qld_bcc
        title = self._normalise.petition_text(data.get("title"))
        code = data.get("reference_id")
        view_url = data.get("url")
        principal = self._normalise.petition_text(data.get("principal"))
        body = data.get("body")
        opened_date = (
            None  # self._normalise.parse_date(data.get("posted_at"), self._tz)
        )
        closed_date = self._normalise.parse_date(data.get("closed_at"), self._tz)

        retrieved_date = self._normalise.parse_date(data.get("retrieved_at"), self._tz)
        signatures = self._norm_signatures(str(data.get("signatures", "")))

        petition, petition_created = PetitionItem.objects.get_or_create(
            source=source,
            code=code,
            defaults={
                "title": title,
                "view_url": view_url,
                "principal": principal,
                "body": body,
                "opened_date": opened_date,
                "closed_date": closed_date,
            },
        )

        change, change_created = PetitionChange.objects.get_or_create(
            petition=petition,
            retrieved_date=retrieved_date,
            defaults={"signatures": signatures},
        )

        return petition, change

    def create_sources(self):
        self._source_au_qld, qld_created = PetitionSource.objects.get_or_create(
            name="au_qld",
            defaults={
                "title": "Queensland Government Petitions",
                "info_url": "https://www.parliament.qld.gov.au/Work-of-the-Assembly/Petitions",
            },
        )
        self._source_au_qld_bcc, bcc_created = PetitionSource.objects.get_or_create(
            name="au_qld_bcc",
            defaults={
                "title": "Brisbane City Council Petitions",
                "info_url": "https://www.epetitions.brisbane.qld.gov.au/",
            },
        )

    def is_au_qld(self, data: dict):
        actual = sorted(data.keys())
        expected = [
            "addressed_to",
            "body",
            "closed_at",
            "eligibility",
            "posted_at",
            "principal",
            "reference_name",
            "reference_num",
            "retrieved_at",
            "signatures",
            "sponsor",
            "subject",
            "url",
        ]
        return actual == expected

    def _is_au_qld_bcc(self, data: dict):
        actual = sorted(data.keys())
        expected = [
            "body",
            "closed_at",
            "principal",
            "reference_id",
            "retrieved_at",
            "sign_uri",
            "signatures",
            "title",
            "url",
        ]
        return actual == expected

    def _norm_signatures(self, value: str):
        value = value.replace("(View signature)", "")
        value = value.replace("\t", "")
        value = value.replace("\r", "")
        value = value.replace("\n", "")
        value = value.replace("signatures", "")
        value = value.replace("signature", "")
        value = value.strip()
        sig = int(value, 10) if value else 0
        if sig < 1:
            a = 1
        return sig
