from pathlib import Path

import pytz

from gather_vision.models import OutageItem
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.component.sqlite_client import SqliteClient


class Outages:
    def __init__(self, logger: Logger, tz: pytz.timezone):
        http_client = HttpClient(logger, use_cache=True)
        normalise = Normalise()

        self._logger = logger
        self._tz = tz

        self._http_client = http_client
        self._normalise = normalise

    def update_outages(self):
        raise NotImplementedError()

    def import_outages(self, path: Path):
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
        if self.is_demand(data):
            return self.import_demand(data)
        elif self.is_summary(data):
            return self.import_summary(data)
        elif self.is_info(data):
            return self.import_info(data)

        raise ValueError()

    def import_demand(self, data: dict):
        demand = data.get("demand")
        rating = data.get("rating")
        retrieved_at = self._normalise.parse_date(data.get("retrieved_at"), self._tz)
        raise NotImplementedError()

    def import_summary(self, data: dict):
        retrieved_at = self._normalise.parse_date(data.get("retrieved_at"), self._tz)
        total_cust = data.get("total_cust")
        updated_at = self._normalise.parse_date(data.get("updated_at"), self._tz)
        raise NotImplementedError()

    def import_info(self, data: dict):
        event_name = data.get("event_name")
        council = data.get("council")
        suburb = data.get("suburb")
        post_code = data.get("post_code")
        cust = data.get("cust")
        cause = data.get("cause")
        streets = data.get("streets")
        restored_date = data.get("restore_at")
        retrieved_date = self._normalise.parse_date(data.get("retrieved_at"), self._tz)

        outage, created = OutageItem.objects.get_or_create(defaults={})
        raise NotImplementedError()

    def is_demand(self, data: dict):
        actual = sorted(data.keys())
        expected = ["demand", "rating", "retrieved_at"]
        return actual == expected

    def is_summary(self, data: dict):
        actual = sorted(data.keys())
        expected = ["retrieved_at", "total_cust", "updated_at"]
        return actual == expected

    def is_info(self, data: dict):
        actual = sorted(data.keys())
        expected = [
            "cause",
            "council",
            "cust",
            "event_name",
            "id",
            "post_code",
            "restore_at",
            "retrieved_at",
            "streets",
            "suburb",
        ]
        return actual == expected
