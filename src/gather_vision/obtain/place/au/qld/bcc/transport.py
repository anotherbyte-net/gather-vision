import dataclasses
import logging
import re
import typing
from datetime import datetime

from gather_vision.apps.explore import models as explore_models
from gather_vision.apps.transport import models as transport_models
from gather_vision.obtain.core import data
from gather_vision.obtain.place.au import area_au
from gather_vision.obtain.place.au.qld import area_qld
from gather_vision.obtain.place.au.qld.bcc import (
    origin_bcc,
    area_bcc,
    area_brisbane,
    tz_bne as tz_bne,
)

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class BrisbaneTranslinkNoticesItem(data.GatherDataItem):
    title: str
    retrieved_date: datetime
    issued_date: datetime
    description: str
    url: str
    start_date: datetime
    stop_date: datetime
    category: str
    severity: str
    locations: list[str]

    groups: list[tuple[str, str]]
    """A list of groups.
    Each group is a (`title`, `category`) pair.
    A `category` must be one of 
    `gather_vision.apps.transport.models.Group.CATEGORY_CHOICES`.
    """

    areas: list[data.GatherDataArea]
    """The `Area` items for the `Event`.
    Each entry is a 
    (`gather_vision.apps.explore.models.Area.LEVEL_CHOICES`, `title`) pair.
    There must be only one instance of each level option.
    """

    origin: data.GatherDataOrigin
    """The data was sourced from this `Origin`.
    Requires a `title`, optional `description` and `url`,
    plus an `areas` entry, which is the same as the :prop:`areas` entry.
    """

    async def save_models(self):
        # origin and origin's area
        origin_area = await explore_models.Area.from_obtain_data(self.origin.areas)
        origin = await explore_models.Origin.from_obtain_data(
            title=self.origin.title,
            description=self.origin.description,
            url=self.origin.url,
            area=origin_area,
        )

        # gatherer
        gatherer = await explore_models.Gatherer.from_obtain_data(
            title=self.gather_name,
            gather_type=self.gather_type,
            description=self.description,
            url=self.url,
        )

        # area
        area = await explore_models.Area.from_obtain_data(self.areas)

        # groups
        groups = []
        for title, category in self.groups:
            groups.append(
                await transport_models.Group.from_obtain_data(title, category)
            )

        await transport_models.Event.from_obtain_data(
            title=self.title,
            retrieved_date=self.retrieved_date,
            issued_date=self.issued_date,
            occurred_date=self.start_date,
            description=self.description,
            url=self.url,
            origin=origin,
            area=area,
            gatherer=gatherer,
            groups=groups,
            start_date=self.start_date,
            stop_date=self.stop_date,
            category=self.category,
            severity=self.severity,
            locations=self.locations,
        )


class BrisbaneTranslinkNoticesWebData(data.WebData):
    # see also: https://translink.com.au/about-translink/open-data
    page_url = "https://translink.com.au/service-updates"
    _notice_url = "https://translink.com.au/service-updates/rss"

    # extract:
    # title - entry title
    # description - entry description
    # issued_date - published date
    # url - link to entry
    # start_date - entry starts affecting date
    # stop_date - entry stops affecting date
    # affected_infra -
    #   infrastructure affected:
    #   gather_vision.apps.transport.models.Event.CATEGORY_CHOICES
    # severity - gather_vision.apps.transport.models.Event.SEVERITY_CHOICES
    # locations - text description of the more precise Area instances
    # services - title (service or line name),
    #   gather_vision.apps.transport.models.Group.CATEGORY_CHOICES
    # areas - locations affected by the event
    # origin - where the data was sourced from

    _descr_patterns = [
        re.compile(
            r"^\((?P<type>[^)]+)\)\s*(?P<description>.+)\.\s*"
            r"Starts\s*affecting:\s*(?P<start_date>.+)\s*"
            r"Finishes affecting:\s*(?P<stop_date>.+)$"
        ),
        re.compile(
            r"^Start\s*date:\s*(?P<start_date>[^a-z]+),\s*"
            r"End\s*date:\s*(?P<stop_date>[^a-z]+),\s*"
            r"Services:\s*(?P<services>.+)$"
        ),
        re.compile(
            r"^\((?P<type>[^)]+)\)\s*(?P<description>.+)\.\s*"
            r"Starts\s*affecting:\s*(?P<start_date>.+)$"
        ),
        re.compile(
            r"^Start\s*date:\s*(?P<start_date>[^a-z]+),\s*"
            r"Services:\s*(?P<services>.+)$"
        ),
        re.compile(
            r"^Affects\s*services:\s*(?P<start_date>[^a-z]+)\s*"
            r"Services:\s*(?P<services>.+)$"
        ),
    ]

    _pattern_group_name = "found"

    @staticmethod
    def _build_re(group_name: str, values: typing.Iterable[str]) -> re.Pattern:
        definition = "|".join(values)
        return re.compile(rf"\b(?P<{group_name}>{definition})\b", re.IGNORECASE)

    _event_durations = _build_re(
        _pattern_group_name,
        [
            "temporary",
            "extended",
            "permanent",
            "weekend",
            "weekday",
            "evening",
            "late night",
        ],
    )
    _event_affected = _build_re(
        _pattern_group_name,
        [
            r"bus\s*stops?",
            "stops?",
            r"bus\s*stations?",
            "stations?",
            r"park\s*('?n'?|and)\s*rides?",
            "tracks?",
            "entrances?",
            r"bus\s*services?",
            "services?",
            "timetables?",
            "platforms?",
            r"bus\s*routes?",
            "routes?",
            r"bus\s*lines?",
            "lines?",
        ],
    )
    _event_changes = _build_re(
        _pattern_group_name,
        [
            "closures?",
            "changes?",
            "disruptions?",
            "diversions?",
            "relocations?",
            "reduced",
            "missed",
            "re-?opened",
            "more",
            "delays?",
            "additional",
            r"free\s*travel",
        ],
    )

    @property
    def name(self):
        return "au-qld-bcc-translink-notices"

    def initial_urls(self) -> typing.Iterable[str]:
        return [self._notice_url]

    def web_resources(
        self, web_data: data.WebDataAvailable
    ) -> typing.Iterable[data.GatherDataRequest | data.GatherDataItem | None]:
        items: dict = web_data.body_data
        for rss_item in items.get("children", {}):
            if rss_item.get("tag") != "channel":
                continue

            doc_info = {}
            for info in rss_item.get("children", {}):
                tag = info.get("tag")
                text = info.get("text", "")
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
                        item_data = self._get_item(
                            {**doc_info}, info.get("children", [])
                        )
                        yield self._build(item_data)
                    case _:
                        pass

    def _get_item(self, info: dict, item: list[dict]) -> dict:
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
                    if "labels" not in info:
                        info["labels"] = set()
                    info["labels"].add(entry.get("text").strip())
        return info

    def _build(self, info: dict) -> BrisbaneTranslinkNoticesItem | None:
        doc_title = info.get("doc_title")
        doc_descr = info.get("doc_descr")
        doc_pub_date = info.get("doc_pub_date")
        doc_build_date = info.get("doc_build_date")

        title = info.get("title")
        descr = info.get("descr")
        link = info.get("link")
        guid = info.get("guid")
        labels = info.get("labels")

        # extract info
        info_descr = self._extract_descr_info(descr)
        info_title = self._extract_title_info(title)
        info_title_new = info_title.get("title_new")
        info_title_affected = info_title.get("event_affected")
        info_title_changes = info_title.get("event_changes")
        info_services = self._extract_service_info(info_descr.get("services", ""))

        # infer item properties from extracted data
        date_parser = BrisbaneTranslinkNoticesItem.datetime_parse
        date_now = BrisbaneTranslinkNoticesItem.datetime_now

        description = ""
        start_date = date_parser(info_descr.get("start_date"), tz_bne)
        stop_date = date_parser(info_descr.get("stop_date"), tz_bne)
        category = transport_models.Event.guess_category(
            "; ".join([*info_title_affected, *info_services])
        )
        severity = transport_models.Event.guess_severity(
            "; ".join([*labels, *info_title_changes])
        )
        groups = list(transport_models.Group.guess_categories(info_services))
        locations = []

        # build the result item
        areas = [area_au, area_qld, area_bcc, area_brisbane]
        return BrisbaneTranslinkNoticesItem(
            gather_name=self.name,
            title=title,
            retrieved_date=date_now(tz_bne),
            issued_date=date_parser(doc_pub_date, tz_bne),
            description=description,
            url=link,
            start_date=start_date,
            stop_date=stop_date,
            category=category,
            severity=severity,
            locations=locations,
            groups=groups,
            areas=areas,
            origin=origin_bcc,
        )

    def _extract_descr_info(self, value: str) -> dict:
        for descr_pattern in self._descr_patterns:
            descr_match = descr_pattern.match(value)
            if descr_match:
                return descr_match.groupdict()

        logger.warning("No match for description '%s'.", value)
        return {}

    def _extract_title_info(self, value: str) -> dict:
        current_title = str(value)
        group_name = self._pattern_group_name
        current_title, event_durations = self._extract_event_info(
            current_title, group_name, self._event_durations
        )
        current_title, event_affected = self._extract_event_info(
            current_title, group_name, self._event_affected
        )
        current_title, event_changes = self._extract_event_info(
            current_title, group_name, self._event_changes
        )

        # known replacement to make in new title
        replacements = {" - ": " ", " for ": " ", " in ": " "}
        for repl_old, repl_new in replacements.items():
            current_title = current_title.replace(repl_old, repl_new)
        current_title = self.str_collapse(current_title)

        return {
            "event_durations": event_durations,
            "event_affected": event_affected,
            "event_changes": event_changes,
            "title_new": current_title,
        }

    def _extract_service_info(self, value: str) -> typing.Iterable[str]:
        services_raw = (value or "").split(",")
        services = [i.strip() for i in services_raw]
        services_more = "..."
        if services_more in services:
            services[services.index(services_more)] = "ELLIPSIS"
        return sorted(services)

    def _extract_event_info(
        self, value: str, name: str, pattern: re.Pattern
    ) -> tuple[str, list[str]]:
        out = str(value)
        found = set()
        while True:
            match = pattern.search(out)
            if not match:
                return out, sorted(found)

            group_value = match.group(name)
            if group_value:
                found.add(group_value.strip().lower())
                index_start = match.start(name)
                index_end = match.end(name)
                out = out[0:index_start].strip() + " " + out[index_end:].strip()
