import hashlib
from pathlib import Path

import pytz
from django.utils.text import slugify

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.component.sqlite_client import SqliteClient
import gather_vision.models as app_models


class Outages:
    def __init__(self, logger: Logger, tz: pytz.timezone):
        http_client = HttpClient(logger, use_cache=True)
        normalise = Normalise()

        self._logger = logger
        self._tz = tz

        self._http_client = http_client
        self._normalise = normalise

    def update_outages(self):
        self.create_sources()
        raise NotImplementedError()

    def import_outages(self, path: Path):
        self._logger.info("Importing outages.")
        self.create_sources()

        db = SqliteClient(path)
        conn = db.get_sqlite_db()
        table_names = list(db.get_table_names(conn))

        results = {}
        for table_name in table_names:
            for row in db.get_table_data(conn, table_name):
                row_keys = list(row.keys())
                row_values = list(row)
                data = dict(zip(row_keys, row_values))
                retrieved_date = data.get("retrieved_at")
                retrieved_date = self._normalise.parse_date(retrieved_date, self._tz)

                if retrieved_date not in results:
                    results[retrieved_date] = {"demand": [], "summary": [], "info": []}

                if self.is_demand(data):
                    demand = self.get_demand(data)
                    results[retrieved_date]["demand"].append(demand)

                elif self.is_summary(data):
                    summary = self.get_summary(data)
                    results[retrieved_date]["summary"].append(summary)

                elif self.is_info(data):
                    info = self.get_info(data)
                    results[retrieved_date]["info"].append(info)
                else:
                    raise ValueError()

        self.import_outage_data(results)
        self._logger.info("Finished importing outages.")

    def get_demand(self, data: dict):
        demand = data.get("demand")
        rating = data.get("rating")
        return {
            "demand_amount": demand,
            "demand_rating": rating,
        }

    def get_summary(self, data: dict):
        total_cust = data.get("total_cust")
        updated_date = self._normalise.parse_date(data.get("updated_at"), self._tz)
        return {
            "customer_count": total_cust,
            "customer_updated_date": updated_date,
        }

    def get_info(self, data: dict):
        event_name = data.get("event_name")
        council = data.get("council")
        suburb = data.get("suburb")
        post_code = data.get("post_code")
        customers = data.get("cust")
        cause = data.get("cause")
        streets = data.get("streets")
        restored_date = self._normalise.parse_date(data.get("restore_at"), self._tz)
        return {
            "event_name": event_name,
            "council": council,
            "suburb": suburb,
            "post_code": post_code,
            "customers": customers,
            "cause": cause,
            "streets": streets,
            "restored_date": restored_date,
        }

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

    def import_outage_data(self, data: dict):
        source = self._source_energex

        groups_seen = 0
        groups_imported = 0
        items_seen = 0
        items_imported = 0

        for retrieved_date, details in data.items():
            demand_data = details.get("demand")
            if len(demand_data) == 1:
                demand_amount = demand_data[0].get("demand_amount")
                demand_rating = demand_data[0].get("demand_rating")
            else:
                demand_amount = 0
                demand_rating = 0

            summary_data = details.get("summary")
            if len(summary_data) == 1:
                customer_count = summary_data[0].get("customer_count")
                updated_date = summary_data[0].get("customer_updated_date")
            else:
                customer_count = 0
                updated_date = None

            group, group_created = app_models.OutageGroup.objects.get_or_create(
                retrieved_date=retrieved_date,
                source_updated_date=updated_date,
                defaults={
                    "demand": demand_amount,
                    "rating": demand_rating,
                    "total_customers": customer_count,
                },
            )
            groups_seen += 1
            if group_created:
                groups_imported += 1

            info_data = details.get("info")
            for info in info_data:
                event_name = info.get("event_name")
                council = info.get("council")
                suburb = info.get("suburb")
                post_code = info.get("post_code")
                customers = info.get("customers")
                cause = info.get("cause")
                streets = info.get("streets")
                restored_date = info.get("restored_date")

                if not event_name:
                    event_name = self._event_name(
                        [
                            i
                            for i in [
                                source.name,
                                str(retrieved_date) if retrieved_date else "",
                                str(updated_date) if updated_date else "",
                                council,
                                suburb,
                                str(post_code) if post_code else "",
                                str(customers) if customers else "",
                                cause,
                                streets,
                                str(restored_date) if restored_date else "",
                            ]
                            if i and i.strip()
                        ]
                    )

                item, item_created = app_models.OutageItem.objects.get_or_create(
                    source=source,
                    group=group,
                    event_name=event_name,
                    defaults={
                        "council": council,
                        "suburb": suburb,
                        "post_code": post_code,
                        "cause": cause,
                        "streets": streets,
                        "restored_date": restored_date,
                        "customers": customers,
                    },
                )
                items_seen += 1
                if item_created:
                    items_imported += 1

            if groups_seen % 200 == 0:
                self._logger.info(
                    f"Running total groups {groups_seen} ({groups_imported} imported) "
                    f"items {items_seen} ({items_imported} imported)."
                )

        self._logger.info(
            f"Groups {groups_seen} ({groups_imported} imported) "
            f"total items {items_seen} ({items_imported} imported)."
        )

    def create_sources(self):
        url = "https://www.energex.com.au"
        (
            self._source_energex,
            energex_created,
        ) = app_models.InformationSource.objects.get_or_create(
            name="energex",
            defaults={"title": "Energex", "info_url": url},
        )

    def _event_name(self, value: list[str]):
        slug = slugify("-".join(value))
        hashed = hashlib.sha256(slug.encode()).hexdigest()
        return hashed
