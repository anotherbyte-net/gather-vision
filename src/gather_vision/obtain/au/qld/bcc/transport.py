import re
import typing
from zoneinfo import ZoneInfo

from gather_vision.obtain.core import data
from gather_vision.obtain.core.data import WebDataAvailable, GatherDataItem


class BrisbaneTranslinkNoticesWebData(data.WebData):
    # from https://translink.com.au/about-translink/open-data
    # see also https://translink.com.au/service-updates
    notice_url = "https://translink.com.au/service-updates/rss"
    page_url = "https://translink.com.au/service-updates"

    summary_patterns = [
        re.compile(
            r"^\((?P<type>[^)]+)\)\s*(?P<description>.+)\.\s*"
            r"Starts\s*affecting:\s*(?P<date_start>.+)\s*Finishes affecting:\s*(?P<date_stop>.+)$"
        ),
        re.compile(
            r"^Start\s*date:\s*(?P<date_start>[^a-z]+),\s*"
            r"End\s*date:\s*(?P<date_stop>[^a-z]+),\s*Services:\s*(?P<services>.+)$"
        ),
        re.compile(
            r"^\((?P<type>[^)]+)\)\s*(?P<description>.+)\.\s*"
            r"Starts\s*affecting:\s*(?P<date_start>.+)$"
        ),
        re.compile(
            r"^Start\s*date:\s*(?P<date_start>[^a-z]+),\s*"
            r"Services:\s*(?P<services>.+)$"
        ),
    ]

    title_patterns = [
        re.compile(
            r"^(?P<location>.+)\s*[:-]\s*temporary\s*stop\s*closure$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^(?P<locations>.+)\s*[:-]\s*temporary\s*stop\s*closures$",
            re.IGNORECASE,
        ),
        re.compile(r"^(?P<location>.+)\s*carpark\s*closure$", re.IGNORECASE),
    ]

    tag_keys = {
        "Current": "When",
        "Upcoming": "When",
        "Minor": "Severity",
        "Major": "Severity",
        "Informative": "EventType",
    }

    @property
    def tags(self) -> dict[str, str]:
        return {}

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.notice_url]

    def web_resources(
        self, web_data: WebDataAvailable
    ) -> typing.Iterable[typing.Union[str, GatherDataItem]]:
        items = web_data.body_data
        for raw_item in items:
            for item in raw_item.get("rss", {}).get("channel", {}).get("item", []):
                event = self.get_event(item)

                # ignore events where the lines are all numbers
                lines = event.lines
                if lines and all(i[-1].isnumeric() for i in lines):
                    continue
                yield event

    def get_event(self, item: dict) -> "TransportEvent":
        tz = self._tz

        tags = []

        # item data
        title = item.get("title", "").strip("⚠ⓘ☒").strip()
        description = self._normalise.extract_html_data(item.get("description"))
        link = item.get("link", "").strip()
        guid = slugify(item.get("guid" "").split("/")[-1])
        categories = item.get("category")

        # links
        if link:
            tags.append(("Link", link))

        # categories
        if isinstance(categories, list):
            for category in categories:
                tags.append((self.tag_keys[category], category))
        elif isinstance(categories, str):
            tags.append((self.tag_keys[categories], categories))
        else:
            raise ValueError()

        # description
        summary_match = self._normalise.regex_match(
            self.summary_patterns, description, unmatched_key="description"
        )

        event_type = summary_match.get("type")
        if event_type:
            tags.append(("EventType", event_type))

        description = summary_match.get("description", "")

        lines = summary_match.get("services", "").split(",")
        lines = sorted([i.strip(" .") for i in lines if i and i.strip(" .")])

        event_start = self._normalise.parse_date(summary_match.get("date_start"), tz)
        event_stop = self._normalise.parse_date(summary_match.get("date_stop"), tz)

        # title data
        title_text = self._normalise.extract_html_data(title)
        title_match = self._normalise.regex_match(
            self.title_patterns, title_text, unmatched_key="description"
        )

        locations = [title_match.get("location")] + title_match.get(
            "locations", ""
        ).split(",")
        locations = [i.strip() for i in locations if i and i.strip()]
        if locations:
            tags.append(("Locations", ", ".join(locations)))

        if self._is_station_closure(title_text):
            tags.append(("Category", "station"))
        if self._is_carpark_closure(title_text):
            tags.append(("Category", "carpark"))
        if self._is_track_closure(title_text):
            tags.append(("Category", "track"))
        if self._is_accessibility_closure(title_text):
            tags.append(("Category", "accessibility"))
        if self._is_stop_closure(description):
            tags.append(("Category", "stop"))

        description += ", " + title_match.get("description", "")
        description = description.strip(" ,")

        result = TransportEvent(
            raw=item,
            title=title,
            description=description if description != title else "",
            tags=tags,
            lines=lines,
            source_id=guid,
            source_name=self.code,
            event_start=event_start,
            event_stop=event_stop,
        )
        return result

    def _is_station_closure(self, value: str):
        value = slugify(value)
        return all(
            [
                "station" in value,
                ("closure" in value or "reopening" in value),
                "park" not in value,
                "escalator" not in value,
                "lift" not in value,
            ]
        )

    def _is_carpark_closure(self, value: str):
        value = slugify(value)
        return all(
            [
                "station" in value,
                ("closure" in value or "changes" in value or "alternatives" in value),
                ("park" in value or "parking" in value),
            ]
        )

    def _is_track_closure(self, value: str):
        value = slugify(value)
        return all(
            [
                "track" in value,
                "closure" in value,
                "park" not in value,
                "car" not in value,
                "station" not in value,
                "escalator" not in value,
                "lift" not in value,
            ]
        )

    def _is_accessibility_closure(self, value: str):
        value = slugify(value)
        return all(
            [
                ("closure" in value or "outage" in value),
                ("lift" in value or "escalator" in value),
            ]
        )

    def _is_stop_closure(self, value: str):
        value = slugify(value)
        return any(
            [
                "temporary-stop-closure" == value,
                "temporary-stop-closures" == value,
            ]
        )
