import re
from datetime import datetime, tzinfo
from typing import Optional

from lxml import html

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.item.contact_trace import ContactTrace


class AuQld:
    """Retrieves and updates info about QLD contact tracing."""

    default_url = "https://www.qld.gov.au/health/conditions/health-alerts/coronavirus-covid-19/current-status/contact-tracing"

    def __init__(
        self,
        logger: logging.Logger,
        timezone: tzinfo,
        http_client: HttpClient,
        url: Optional[str] = None,
    ):
        self._logger = logger
        self._timezone = timezone
        self._url = url or self.default_url
        self._http_client = http_client

    def get_new_items(self):
        response = self.get_page()
        last_updated, rows = self.get_data(response)
        items = self.get_items(rows)
        return items

    def get_page(self):
        return self._http_client.get(self._url)

    def get_data(self, response):
        tree = html.fromstring(response.text)

        if tree is None:
            raise ValueError("No html available.")

        marker = tree.xpath('//div[@id="newrows-202041"]')
        if len(marker) != 1:
            raise ValueError("Could not find marker.")

        marker = marker[0]

        last_updated = marker.xpath("./preceding-sibling::p/text()")
        if len(last_updated) < 1:
            raise ValueError("Could not find paras.")

        last_updated = last_updated[-1]
        if "This table last updated" not in last_updated:
            raise ValueError("Could not find last updated.")

        table = marker.xpath(".//table")
        if len(table) != 1:
            raise ValueError("Could not find table.")

        table = table[0]

        rows = table.xpath(".//tbody//tr")
        return last_updated, rows

    def get_items(self, rows):
        date_retrieved = datetime.now(tz=self._timezone)

        for row in rows:
            data_date = row.get("data-date")
            data_lgas = row.get("data-lgas")
            # data_advice = row.get("data-advice")
            # data_location = row.get("data-location")
            # data_address = row.get("data-address")
            # data_suburb = row.get("data-suburb")
            # data_datetext = row.get("data-datetext")
            # data_timetext = row.get("data-timetext")

            # e.g. '2021-12-19T15:35'
            data_added = datetime.strptime(
                self._tidy(row.get("data-added")), "%Y-%m-%dT%H:%M"
            )

            cells = row.xpath("./td")

            td_exposure_date = cells[0].text

            # td_place = cells[1].xpath(".//text()")
            td_location = cells[1].xpath('./span[@class="location"]')
            if len(td_location) == 1:
                td_location = td_location[0].text
            else:
                td_location = None

            td_address = cells[1].xpath('./span[@class="address"]')
            if len(td_address) == 1:
                td_address = td_address[0].text
            else:
                td_address = None

            td_suburb = cells[2].text
            td_exposure_times = cells[3].text
            td_category = cells[4].text

            start_datetime, stop_datetime = self._parse_exposures(
                data_date, td_exposure_date, td_exposure_times
            )

            yield ContactTrace(
                start_datetime=start_datetime,
                stop_datetime=stop_datetime,
                added_datetime=data_added,
                retrieved_datetime=date_retrieved,
                category=self._tidy(td_category),
                lgas=self._tidy(data_lgas),
                suburb=self._tidy(td_suburb),
                location=self._tidy(td_location),
                address=self._tidy(td_address),
            )

    def _parse_exposures(
        self,
        data_date: str,
        td_exposure_date: str,
        td_exposure_times: str,
    ):
        # td date
        # e.g. 'Sunday 19 December 2021'
        parsed_date = datetime.strptime(self._tidy(td_exposure_date), "%A %d %B %Y")

        # td times
        # e.g. '11.32am - 11.40am': '11.32am' and '11.40am'
        parsed_times = []
        for i in td_exposure_times.split(" - "):
            parsed = False
            for pattern in ["%I.%M%p", "%I%p"]:
                try:
                    parsed_times.append(datetime.strptime(i, pattern))
                    parsed = True
                except ValueError:
                    continue
            if not parsed:
                raise ValueError(f"Could not parse '{i}'.")

        if not parsed_times:
            raise ValueError()

        # date datetime start
        # e.g. '2021-12-19T15:35'
        parsed_datetime_start = datetime.strptime(
            self._tidy(data_date), "%Y-%m-%dT%H:%M"
        )
        parsed_datetime_start = parsed_datetime_start.replace(tzinfo=self._timezone)

        if len(parsed_times) > 0:
            start_datetime = datetime(
                parsed_date.year,
                parsed_date.month,
                parsed_date.day,
                parsed_times[0].hour,
                parsed_times[0].minute,
                tzinfo=self._timezone,
            )
        else:
            raise ValueError()

        if parsed_datetime_start != start_datetime:
            raise ValueError()

        if len(parsed_times) == 2:
            stop_datetime = datetime(
                parsed_date.year,
                parsed_date.month,
                parsed_date.day,
                parsed_times[1].hour,
                parsed_times[1].minute,
                tzinfo=self._timezone,
            )

        else:
            stop_datetime = start_datetime

        return start_datetime, stop_datetime

    def _tidy(self, value: str):
        if not value or not value.strip():
            return ""
        value = value.strip()
        value = re.sub(r"\s+", " ", value)
        return value
