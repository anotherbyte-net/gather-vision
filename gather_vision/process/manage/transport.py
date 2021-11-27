import csv

from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional

import pytz
from django.utils import timezone
from django.utils.text import slugify
import icalendar as cal

from gather_vision.process.component.html_extract import HtmlExtract
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.ical import ICal
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.item.transport_event import TransportEvent
from gather_vision.process.service.qld_rail_events import QldRailEvents
from gather_vision.process.service.translink_notices import TranslinkNotices


class Transport:

    train_lines = {
        "ferny-grove": "D02130",
        "beenleigh": "D02130",
        "shorncliffe": "00467E",
        "cleveland": "00467E",
        "airport": "FFC420",
        "gold-coast": "FFC420",
        "caboolture": "008752",
        "sunshine-coast": "008752",
        "ipswich": "008752",
        "rosewood": "008752",
        "ipswichrosewood": "008752",
        "redcliffe-peninsula": "0B79BD",
        "springfield": "0B79BD",
        "doomben": "A5449A",
        "inner-city": "FFFFFF",
    }

    def __init__(self, logger: Logger, tz: pytz.timezone):
        http_client = HttpClient(logger, use_cache=True)
        normalise = Normalise()
        html_extract = HtmlExtract()

        self._logger = logger
        self._tz = tz

        self._http_client = http_client
        self._normalise = normalise
        self._html_extract = html_extract
        self._tl = TranslinkNotices(logger, http_client, normalise, html_extract, tz)
        self._qr = QldRailEvents(logger, http_client, normalise, html_extract, tz)

    def update_events(self):
        now = timezone.now() - timedelta(days=3)

        events = []
        for event in self._tl.fetch():
            if not self.filter(event, now):
                continue
            events.append(event)
        for event in self._qr.fetch():
            if not self.filter(event, now):
                continue
            events.append(event)

        events = sorted(events, key=lambda x: x.sort_str)

        for event in events:
            for line in event.lines:
                line_str = str(line)
                if line_str.endswith(" Line"):
                    line_str = line_str[0:-5]
                line_str = slugify(line_str)
                if line_str in self.train_lines:
                    event.tags.append(("IsTrain", "Yes"))
                    break

        # self.export_ics(Path("seq-train-events.ics"), events)
        # self.export_csv(Path("seq-train-events.csv"), events)
        raise NotImplementedError()

    def filter(
        self, event: TransportEvent, start_date: datetime
    ) -> Optional[TransportEvent]:
        has_start = event.event_start is not None
        has_stop = event.event_stop is not None
        if not has_start and not has_stop:
            # ignore events with no dates
            return None

        elif has_stop and event.event_stop < start_date:
            # ignore events where the stop is before the filter date
            return None

        # include events where start date is before filter date
        # as some events have only start dates (continuing events)
        return event

    def generate_ics(self, events: Iterable[TransportEvent]) -> cal.Calendar:
        descr = "Changes and closures in the Brisbane public transport network."
        calendar = ICal(
            provider="gather-vision",
            title="Brisbane Public Transport Notices",
            description=descr,
            tz="Australia/Brisbane",
            ttl="PT6H",
        )

        for event in events:
            calendar.add_event(
                title=event.title,
                body=event.description,
                date_start=event.event_start,
                date_stop=event.event_stop or event.event_start,
                location="",
                url="",
                uid="",
                date_stamp="",
                date_modified="",
                date_created="",
                sequence_num="",
            )

        return calendar.get_calendar()

    def export_ics(self, path: Path, events: Iterable[TransportEvent]) -> None:
        c = self.generate_ics(events)
        path.write_text(c.to_ical(), encoding="utf-8")

    def export_csv(self, path: Path, events: Iterable[TransportEvent]) -> None:
        with open(path, "wt", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, TransportEvent.cvs_headers())
            writer.writeheader()
            for event in events:
                writer.writerow(event.csv_row)
