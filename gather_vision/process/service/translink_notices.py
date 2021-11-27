import io
import re
from datetime import tzinfo

import feedparser
from django.utils.text import slugify
from requests_cache import CachedSession

from gather_vision.process.component.html_extract import HtmlExtract
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.item.transport_event import TransportEvent


class TranslinkNotices:
    code = "translink"

    # from https://translink.com.au/about-translink/open-data
    # see also https://translink.com.au/service-updates
    notice_url = "https://translink.com.au/service-updates/rss"

    summary_patterns = [
        re.compile(
            r"^\((?P<type>[^)]+)\)\s*(?P<description>.+)\.\s*Starts\s*affecting:\s*(?P<date_start>.+)$"
        ),
        re.compile(
            r"^Start\s*date:\s*(?P<date_start>[^a-z]+),\s*Services:\s*(?P<services>.+)$"
        ),
        re.compile(
            r"^Start\s*date:\s*(?P<date_start>[^a-z]+),\s*End\s*date:\s*(?P<date_stop>[^a-z]+),\s*Services:\s*(?P<services>.+)$"
        ),
    ]

    title_patterns = [
        re.compile(
            r"^(?P<location>.+)\s*[:-]\s*(?P<category>temporary\s*stop\s*closure)$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^(?P<locations>.+)\s*[:-]\s*(?P<category>temporary\s*stop\s*closures)$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^(?P<location>.+)\s*(?P<category>carpark\s*closure)$", re.IGNORECASE
        ),
    ]

    tag_keys = {
        "Upcoming": "When",
        "Minor": "Severity",
        "Major": "Severity",
        "Informative": "EventType",
    }

    def __init__(
        self,
        logger: Logger,
        http_client: HttpClient,
        normalise: Normalise,
        html_extract: HtmlExtract,
        tz: tzinfo,
    ):
        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._html_extract = html_extract
        self._tz = tz

    def fetch(self):
        items = self.get_data()
        for item in items.entries:
            event = self.get_event(item)

            # ignore events where the lines are all numbers
            lines = event.lines
            if lines and all(i[-1].isnumeric() for i in lines):
                continue
            yield event

    def get_data(self):
        s = CachedSession("http_cache", backend="filesystem", use_cache_dir=True)

        # use requests to do the actual request
        r = s.get(self.notice_url)

        # build the info for feedparser
        content = io.BytesIO(r.content)
        etag = r.headers.get("etag")
        last_mod = r.headers.get("last-modified")
        resp_headers = r.headers
        if "content-location" not in resp_headers:
            resp_headers["content-location"] = r.url
        d = feedparser.parse(
            content,
            etag=etag,
            modified=last_mod,
            response_headers=resp_headers,
        )

        return d

    def get_event(self, item: dict) -> TransportEvent:
        tz = self._tz

        tags = []

        # item data
        source_id = slugify(item.get("id", "").split("/")[-1])
        summary = item.get("summary", "")
        link = item.get("link", "").strip()
        item_tags = item.get("tags", {})
        title = item.get("title", "").strip("⚠ⓘ☒").strip()

        if link:
            tags.append(("Link", link))

        for tag in item_tags:
            tag_term = tag.get("term")
            tag_label = tag.get("label")
            if tag_label:
                raise ValueError()
            tags.append((self.tag_keys[tag_term], tag_term))

        # summary data
        summary_text = self._html_extract.get_data(summary)
        summary_match = self._normalise.regex_match(
            self.summary_patterns, summary_text, unmatched_key="description"
        )

        event_type = summary_match.get("type")
        if event_type:
            tags.append(("EventType", event_type))

        description = summary_match.get("description")

        lines = summary_match.get("services", "").split(",")
        lines = sorted([i.strip(" .") for i in lines if i and i.strip(" .")])

        event_start = self._normalise.parse_date(summary_match.get("date_start"), tz)
        event_stop = self._normalise.parse_date(summary_match.get("date_stop"), tz)

        # title data
        title_text = self._html_extract.get_data(title)
        title_match = self._normalise.regex_match(
            self.title_patterns, title_text, unmatched_key="description"
        )

        locations = [title_match.get("location")] + title_match.get(
            "locations", ""
        ).split(",")
        locations = [i.strip() for i in locations if i and i.strip()]
        if locations:
            tags.append(("Locations", ", ".join(locations)))

        category = title_match.get("category")
        if category:
            tags.append(("Category", category))

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
