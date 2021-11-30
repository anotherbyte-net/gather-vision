import pytz
from django.utils import timezone
from django.utils.text import slugify

import gather_vision.models as app_models
from gather_vision.process.component.html_extract import HtmlExtract
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise


class EnergexEvents:
    code = "energex"

    base_url = "https://www.energex.com.au"
    api_url = f"{base_url}/api/outages/v0.3"
    usage_url = f"{base_url}/static/Energex/Network%20Demand/networkdemand.txt"
    outage_summary_url = f"{api_url}/summary"
    outage_councils_url = f"{api_url}/council"
    outage_council_suburbs_url = f"{api_url}/suburb"
    outage_suburb_url = f"{api_url}/search"

    def __init__(
        self,
        logger: Logger,
        http_client: HttpClient,
        normalise: Normalise,
        html_extract: HtmlExtract,
        tz: pytz.timezone,
    ):
        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._html_extract = html_extract
        self._tz = tz

        self._source = app_models.InformationSource.objects.get(name=self.code)

    def update_outages(self):
        self._logger.info("Updating outages.")

        groups_seen = 0
        groups_imported = 0
        items_seen = 0
        items_imported = 0

        retrieved_date = timezone.now()

        usage = self.update_usage()
        demand_amount = usage.get("demand")
        demand_rating = usage.get("rating")

        summary = self.update_summary()
        customer_count = summary.get("total_cust")
        updated_date = summary.get("updated_date")

        group, group_created = app_models.OutageGroup.objects.get_or_create(
            source_updated_date=updated_date,
            defaults={
                "retrieved_date": retrieved_date,
                "demand": demand_amount,
                "rating": demand_rating,
                "total_customers": customer_count,
            },
        )
        groups_seen += 1
        if group_created:
            groups_imported += 1

        for event in self.update_events():
            event_name = event.get("event_name")
            council = event.get("council")
            suburb = event.get("suburb")
            post_code = event.get("post_code")
            customers = event.get("cust")
            cause = event.get("cause")
            restored_date = event.get("restore_date")
            streets = event.get("streets")
            item, item_created = app_models.OutageItem.objects.update_or_create(
                source=self._source,
                event_name=event_name,
                defaults={
                    "group": group,
                    "council": council or "",
                    "suburb": suburb or "",
                    "post_code": post_code or "",
                    "cause": cause or "",
                    "streets": streets or "",
                    "restored_date": restored_date,
                    "customers": customers or "",
                },
            )
            items_seen += 1
            if item_created:
                items_imported += 1

        if groups_seen % 10 == 0:
            self._logger.info(
                f"Running total groups {groups_seen} ({groups_imported} imported) "
                f"items {items_seen} ({items_imported} imported)."
            )

        self._logger.info(
            f"Groups {groups_seen} ({groups_imported} imported) "
            f"total items {items_seen} ({items_imported} imported)."
        )

        self._logger.info("Finished updating outages.")

    def update_usage(self):
        r = self._http_client.get(self.usage_url)
        demand = r.text
        rating = self.demand_rating(demand)
        return {
            "demand": demand,
            "rating": rating,
        }

    def update_summary(self):
        r = self._http_client.get(self.outage_summary_url)
        summary = r.json()
        data = summary.get("data", {})
        total_cust = data.get("totalCustomersAffected", 0)

        updated_at = data.get("lastUpdated", "")
        updated_at = self._normalise.parse_date(updated_at, self._tz)

        return {
            "total_cust": total_cust,
            "updated_date": updated_at,
        }

    def update_events(self):
        r = self._http_client.get(self.outage_councils_url, params={"council": ""})
        councils = r.json().get("data", [])
        for council in councils:
            council_name = council.get("name", "")

            r = self._http_client.get(
                self.outage_council_suburbs_url,
                params={"council": council_name, "suburb": ""},
            )
            suburbs = r.json().get("data", [])
            for suburb in suburbs:
                suburb_name = suburb.get("name", "")

                r = self._http_client.get(
                    self.outage_suburb_url, params={"suburb": suburb_name}
                )
                events = r.json().get("data", [])
                for event in events:
                    restore_date = self._normalise.parse_date(
                        event.get("restoreTime", "").replace(":", ""), self._tz
                    )
                    streets = str.join(
                        ",", sorted(s.title() for s in event.get("streets", []))
                    )
                    yield {
                        "event_name": slugify(event.get("event", "")),
                        "council": event.get("council", "").title(),
                        "suburb": event.get("suburb", "").title(),
                        "post_code": event.get("postcode", ""),
                        "cust": event.get("customersAffected", ""),
                        "cause": event.get("cause", ""),
                        "restore_date": restore_date,
                        "streets": streets,
                    }

    def demand_rating(self, demand: str):
        demand = int(demand)

        # demand min: 0, demand max: 5500
        # found in:
        # https://www.energex.com.au/__data/assets/js_file_folder/0011/653996/main.js?version=0.3.59

        # divided into 4 equal parts: low, moderate, high, extreme
        # then into 3 parts = approx 458.3 per smallest part
        # demand_min = 0
        demand_max = 5500
        rating_min = 1
        rating_max = 12

        demand_part = demand_max / 4 / 3
        rating = int(demand / demand_part)

        if rating < rating_min:
            rating = rating_min

        if rating > rating_max:
            rating = rating_max

        return rating
