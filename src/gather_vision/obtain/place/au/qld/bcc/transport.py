import dataclasses
import re
import typing
from datetime import datetime
from zoneinfo import ZoneInfo

from django.utils.text import slugify

from gather_vision.obtain.core import data
from gather_vision.obtain.core.data import WebDataAvailable, GatherDataItem


@dataclasses.dataclass(frozen=True)
class BrisbaneTranslinkNoticesItem(data.GatherDataItem):
    event: typing.Optional[str]
    description: typing.Optional[str]
    locations: typing.Optional[list[str]]
    services: typing.Optional[list[str]]
    date_start: typing.Optional[datetime]
    date_stop: typing.Optional[datetime]
    date_published: typing.Optional[datetime]
    url: typing.Optional[str]
    id: typing.Optional[str]
    categories: typing.Optional[set[str]]


class BrisbaneTranslinkNoticesWebData(data.WebData):
    # from https://translink.com.au/about-translink/open-data
    # see also https://translink.com.au/service-updates
    notice_url = "https://translink.com.au/service-updates/rss"
    page_url = "https://translink.com.au/service-updates"

    descr_patterns = [
        re.compile(
            r"^\((?P<type>[^)]+)\)\s*(?P<description>.+)\.\s*"
            r"Starts\s*affecting:\s*(?P<date_start>.+)\s*"
            r"Finishes affecting:\s*(?P<date_stop>.+)$"
        ),
        re.compile(
            r"^Start\s*date:\s*(?P<date_start>[^a-z]+),\s*"
            r"End\s*date:\s*(?P<date_stop>[^a-z]+),\s*"
            r"Services:\s*(?P<services>.+)$"
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
            r"^(?P<location>.+)\s*[:-]\s*" r"(?P<event>temporary\s*stop\s*closure)$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^(?P<locations>.+)\s*[:-]\s*" r"(?P<event>temporary\s*stop\s*closure)s$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^(?P<location>.+)\s*" r"(?P<event>carpark\s*closure)$",
            re.IGNORECASE,
        ),
    ]

    tag_keys = {
        "Current": "When",
        "Upcoming": "When",
        "Minor": "Severity",
        "Major": "Severity",
        "Informative": "EventType",
    }

    @property
    def name(self):
        return "au-qld-bcc-translink-notices"

    @property
    def tags(self) -> dict[str, str]:
        return {
            "country": "Australia",
            "region": "Queensland",
            "district": "Brisbane City Council",
            "locality": "City of Brisbane",
            "data_source_location": "web",
            "data_source_category": "transport",
            "data_source_owner": "TransLink",
        }

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.notice_url]

    def web_resources(
        self, web_data: WebDataAvailable
    ) -> typing.Iterable[typing.Union[str, GatherDataItem]]:
        items = web_data.body_data
        for rss_item in items.get("children"):
            if rss_item.get("tag") != "channel":
                continue

            doc_info = {}
            for info in rss_item.get("children"):
                tag = info.get("tag")
                text = info.get("text")
                match tag:
                    case "title":
                        doc_info["doc_title"] = text
                    case "description":
                        doc_info["doc_descr"] = text
                    case "pubDate":
                        doc_info["doc_pub_date"] = text
                    case "lastBuildDate":
                        doc_info["doc_build_date"] = text
                    case "item":
                        yield self._get_item(doc_info, info.get("children"))
                        doc_info = {}

    def _get_item(self, info: dict, item: list[dict]) -> BrisbaneTranslinkNoticesItem:
        for entry in item:
            match entry.get("tag"):
                case "title":
                    info["title"] = entry.get("text").strip("⚠ⓘ☒").strip()
                case "description":
                    info["descr"] = entry.get("text").strip()
                case "link":
                    info["link"] = entry.get("text").strip()
                case "guid":
                    info["guid"] = entry.get("text").split("/")[-1].strip()
                case "category":
                    if "categories" not in info:
                        info["categories"] = set()
                    info["categories"].add(entry.get("text").strip())
        return self._build(info)

    def _build(self, info: dict) -> BrisbaneTranslinkNoticesItem:
        doc_title = info.get("doc_title")
        doc_descr = info.get("doc_descr")
        doc_pub_date = info.get("doc_pub_date")
        doc_build_date = info.get("doc_build_date")
        title = info.get("title").strip()
        descr = info.get("descr")
        link = info.get("link")
        guid = info.get("guid")
        categories = info.get("categories")

        # extract info from description
        descr_match = None
        for descr_pattern in self.descr_patterns:
            descr_match = descr_pattern.match(descr)
            if descr_match:
                break

        if descr_match:
            groups = descr_match.groupdict()
            if "type" in groups:
                info["EventType"] = groups.get("type")

            if "description" in groups:
                info["descr_precise"] = groups.get("description")

            if "services" in groups:
                services_raw = (groups.get("services") or "").split(",")
                services = [i.strip() for i in services_raw]
                services_more = "..."
                if services_more in services:
                    services[services.index(services_more)] = "ALL"
                info["lines"] = sorted(services)

            if "date_start" in groups:
                info["date_start"] = groups.get("date_start")

            if "date_stop" in groups:
                info["date_stop"] = groups.get("date_stop")

        # extract info from title
        title_match = None
        for title_pattern in self.title_patterns:
            title_match = title_pattern.match(title)
            if title_match:
                break

        if title_match:
            groups = title_match.groupdict()
            if "location" in groups:
                info["locations"] = [groups.get("location").strip()]
            if "locations" in groups:
                info["locations"] = [groups.get("locations").split(",")]
            if "event" in groups:
                info["event"] = groups.get("event")

        # infer details from title
        if self._is_station_closure(title):
            categories.add("Station")
        if self._is_carpark_closure(title):
            categories.add("Carpark")
        if self._is_track_closure(title):
            categories.add("Track")
        if self._is_accessibility_closure(title):
            categories.add("Accessibility")
        if self._is_stop_closure(descr):
            categories.add("Stop")

        # TODO: what are these?
        # if info.get("descr_precise"):
        #     pass
        # if info.get("EventType"):
        #     pass

        return BrisbaneTranslinkNoticesItem(
            gather_name=self.name,
            tags=self.tags,
            event=title,
            description=info.get("event"),
            locations=info.get("locations"),
            services=info.get("lines"),
            date_start=self._parse_date(info.get("date_start")),
            date_stop=self._parse_date(info.get("date_stop")),
            id=guid,
            url=link,
            date_published=self._parse_date(doc_pub_date),
            categories=categories,
        )

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

    def _parse_date(self, value: str) -> typing.Optional[datetime]:
        if not value or not value.strip():
            return None
        options = ["%d/%m/%Y %I:%M %p", "%I:%M %p", "%a, %d %b %Y %H:%M:%S %z"]
        for option in options:
            try:
                parsed = datetime.strptime(value, option)
                result = parsed.replace(tzinfo=ZoneInfo("Australia/Brisbane"))
                return result
            except ValueError:
                continue
        raise ValueError(f"Cannot parse datetime '{value}'.")

    # def get_event(self, item: dict) -> "TransportEvent":
    #     tz = self._tz
    #
    #     tags = []
    #
    #     # item data
    #     title = item.get("title", "").strip("⚠ⓘ☒").strip()
    #     description = self._normalise.extract_html_data(item.get("description"))
    #     link = item.get("link", "").strip()
    #     guid = slugify(item.get("guid" "").split("/")[-1])
    #     categories = item.get("category")
    #
    #     # links
    #     if link:
    #         tags.append(("Link", link))
    #
    #     # categories
    #     if isinstance(categories, list):
    #         for category in categories:
    #             tags.append((self.tag_keys[category], category))
    #     elif isinstance(categories, str):
    #         tags.append((self.tag_keys[categories], categories))
    #     else:
    #         raise ValueError()
    #
    #     # description
    #     summary_match = self._normalise.regex_match(
    #         self.summary_patterns, description, unmatched_key="description"
    #     )
    #
    #     event_type = summary_match.get("type")
    #     if event_type:
    #         tags.append(("EventType", event_type))
    #
    #     description = summary_match.get("description", "")
    #
    #     lines = summary_match.get("services", "").split(",")
    #     lines = sorted([i.strip(" .") for i in lines if i and i.strip(" .")])
    #
    #     event_start = self._normalise.parse_date(summary_match.get("date_start"), tz)
    #     event_stop = self._normalise.parse_date(summary_match.get("date_stop"), tz)
    #
    #     # title data
    #     title_text = self._normalise.extract_html_data(title)
    #     title_match = self._normalise.regex_match(
    #         self.title_patterns, title_text, unmatched_key="description"
    #     )
    #
    #     locations = [title_match.get("location")] + title_match.get(
    #         "locations", ""
    #     ).split(",")
    #     locations = [i.strip() for i in locations if i and i.strip()]
    #     if locations:
    #         tags.append(("Locations", ", ".join(locations)))
    #
    #     if self._is_station_closure(title_text):
    #         tags.append(("Category", "station"))
    #     if self._is_carpark_closure(title_text):
    #         tags.append(("Category", "carpark"))
    #     if self._is_track_closure(title_text):
    #         tags.append(("Category", "track"))
    #     if self._is_accessibility_closure(title_text):
    #         tags.append(("Category", "accessibility"))
    #     if self._is_stop_closure(description):
    #         tags.append(("Category", "stop"))
    #
    #     description += ", " + title_match.get("description", "")
    #     description = description.strip(" ,")
    #
    #     result = TransportEvent(
    #         raw=item,
    #         title=title,
    #         description=description if description != title else "",
    #         tags=tags,
    #         lines=lines,
    #         source_id=guid,
    #         source_name=self.code,
    #         event_start=event_start,
    #         event_stop=event_stop,
    #     )
    #     return result
