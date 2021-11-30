import json

import pytz
from django.utils.text import slugify

from gather_vision.process.component.html_extract import HtmlExtract
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.item.transport_event import TransportEvent


class QldRailEvents:
    code = "qldrail"

    page_url = (
        "https://www.queenslandrail.com.au/forcustomers/trackclosures/12monthcalendar"
    )
    cal_url = "https://www.queenslandrail.com.au/SPWebApp/api/ContentQuery/GetItems"
    params = {
        "WebUrl": "/Customers",
        "ListName": "Planned Track Closings",
        "ViewFields": [
            "Title",
            "Description",
            "EventDate",
            "EndDate",
            "ID",
            "TrackClosureName0",
            "LineAffected",
            "fRecurrence",
            "fAllDayEvent",
            "WorksInclude",
            "Is_x0020_CRR_x0020_Event",
        ],
        "RowLimit": 3000,
    }
    headers = {
        "Accept": "application/json",
        "Host": "www.queenslandrail.com.au",
        "Origin": "https://www.queenslandrail.com.au",
        "Referer": "https://www.queenslandrail.com.au/forcustomers/trackclosures/12monthcalendar",  # noqa: E501
    }

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

    def fetch(self):
        items = self.get_items()
        for item in items:
            yield self.get_event(item)

    def get_items(self):
        # GET first to populate cookies
        self._http_client.get(self.page_url)
        # POST to retrieve event data
        r2 = self._http_client.post(
            self.cal_url, json=self.params, headers=self.headers
        )
        # the json has syntax errors
        fix_syntax_errors = r2.text.replace('\\":,', '\\":\\"\\",')
        items = json.loads(json.loads(fix_syntax_errors))
        return items

    def get_event(self, item: dict) -> TransportEvent:
        tags = self.get_links(item)

        all_day = item.get("fAllDayEvent")
        if all_day is True or all_day == "True":
            tags.append(("AllDayEvent", "Yes"))

        recurrence = item.get("fRecurrence")
        if recurrence != "False":
            tags.append(("IsReoccurrence", "Yes"))

        crr = item.get("Is_x0020_CRR_x0020_Event")
        if crr is True or crr == "True":
            tags.append(("IsDueToCrossRiverRail", "Yes"))

        tags.append(("Severity", "Major"))
        tags.append(("Category", "track"))

        title = item.get("Title", "")
        description = self.get_description(item)
        source_id = slugify(item.get("ID"))
        lines = self.get_lines(item)
        event_start = self._normalise.parse_date(item.get("EventDate"), self._tz)
        event_stop = self._normalise.parse_date(item.get("EndDate"), self._tz)

        result = TransportEvent(
            raw=item,
            title=title,
            description=description,
            tags=tags,
            lines=lines,
            source_id=source_id,
            source_name=self.code,
            event_start=event_start,
            event_stop=event_stop,
        )
        return result

    def get_description(self, data: dict) -> str:
        items = [data.get("Description"), data.get("WorksInclude")]
        items = [i for i in items if i]
        result = "; ".join(items).strip(" ;")
        return result

    def get_links(self, data: dict) -> list[tuple[str, str]]:
        result = []

        raw = data.get("TrackClosureName0")

        service_updates_url = "https://translink.com.au/service-updates"

        for url, title in self._html_extract.get_url_text(raw):
            if url == service_updates_url:
                continue
            if url:
                result.append((url, title))

        return result

    def get_lines(self, data: dict) -> list[str]:
        result = data.get("LineAffected", "").split(";#")
        result = [i for i in result if i]
        return result
