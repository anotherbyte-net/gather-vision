from pathlib import Path

from zoneinfo import ZoneInfo

from gather_vision import models as app_models
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.component.sqlite_client import SqliteClient
from gather_vision.process.service.petitions_au_qld import PetitionsAuQld
from gather_vision.process.service.petitions_au_qld_bcc import PetitionsAuQldBcc


class PetitionImport:
    def __init__(self, logger: Logger, normalise: Normalise, tz: ZoneInfo):
        self._logger = logger
        self._normalise = normalise
        self._tz = tz

        self._source_au_qld = app_models.InformationSource.objects.get(
            name=PetitionsAuQld.code
        )
        self._source_au_qld_bcc = app_models.InformationSource.objects.get(
            name=PetitionsAuQldBcc.code
        )

    def import_petitions(self, path: Path):
        self._logger.info("Importing petitions.")

        petitions_seen = 0
        petitions_imported = 0
        changes_seen = 0
        changes_imported = 0

        db = SqliteClient(path)
        conn = db.get_sqlite_db()
        table_names = list(db.get_table_names(conn))
        for table_name in table_names:
            for row in db.get_table_data(conn, table_name):
                row_keys = list(row.keys())
                row_values = list(row)
                data = dict(zip(row_keys, row_values))

                if self.is_au_qld(data):
                    (
                        petition,
                        petition_created,
                        change,
                        change_created,
                    ) = self.import_au_qld(data)
                elif self._is_au_qld_bcc(data):
                    (
                        petition,
                        petition_created,
                        change,
                        change_created,
                    ) = self.import_au_qld_bcc(data)
                else:
                    raise ValueError("Unrecognised data format.")

                petitions_seen += 1
                if petition_created:
                    petitions_imported += 1

                changes_seen += 1
                if change_created:
                    changes_imported += 1

                if petitions_seen % 1000 == 0:
                    self._logger.info(
                        f"Running total petitions {petitions_seen} "
                        f"({petitions_imported} imported) "
                        f"changes {changes_seen} ({changes_imported} imported)."
                    )

        self._logger.info(
            f"petitions {petitions_seen} ({petitions_imported} imported) "
            f"changes {changes_seen} ({changes_imported} imported)."
        )
        self._logger.info("Finished importing petitions.")

    def import_au_qld(self, data: dict):
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

        petition, petition_created = app_models.PetitionItem.objects.get_or_create(
            source=self._source_au_qld,
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

        change, change_created = app_models.PetitionChange.objects.get_or_create(
            petition=petition,
            retrieved_date=retrieved_date,
            defaults={"signatures": signatures},
        )

        return petition, petition_created, change, change_created

    def import_au_qld_bcc(self, data: dict):
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
        signatures = self._normalise.norm_signatures(str(data.get("signatures", "")))

        petition, petition_created = app_models.PetitionItem.objects.get_or_create(
            source=self._source_au_qld_bcc,
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

        change, change_created = app_models.PetitionChange.objects.get_or_create(
            petition=petition,
            retrieved_date=retrieved_date,
            defaults={"signatures": signatures},
        )

        return petition, petition_created, change, change_created

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
