from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from django.utils import timezone
from django.utils.text import slugify

from gather_vision import models as app_models
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.item.transport_event import TransportEvent
from gather_vision.process.service.transport.qld_rail_events import QldRailEvents
from gather_vision.process.service.transport.translink_notices import TranslinkNotices


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

    def __init__(self, logger: Logger, tz: ZoneInfo, http_client: HttpClient):
        normalise = Normalise()

        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._tz = tz

    def run_update(self):
        self._logger.info("Updating transport notices.")
        self.create_au_qld_translink()
        self.create_au_qld_rail()

        tl = TranslinkNotices(
            self._logger,
            self._http_client,
            self._normalise,
            self._tz,
        )
        qr = QldRailEvents(
            self._logger,
            self._http_client,
            self._normalise,
            self._tz,
        )

        month_ago = timezone.now() - timedelta(days=30)

        sources = {
            TranslinkNotices.code: app_models.InformationSource.objects.get(
                name=TranslinkNotices.code
            ),
            QldRailEvents.code: app_models.InformationSource.objects.get(
                name=QldRailEvents.code
            ),
        }

        events_seen = 0
        events_created = 0
        events_updated = 0

        events = self.get_events(tl, qr, month_ago)
        for event in events:
            self._tidy(event)
            obj, created = self.update_event(sources, event)

            events_seen += 1
            if created:
                events_created += 1
            else:
                events_updated += 1

            if events_seen % 20 == 0:
                self._logger.info(
                    f"Running total notices {events_seen} "
                    f"({events_updated} updated, {events_created} created)."
                )

        self._logger.info(
            f"Notices {events_seen} "
            f"({events_updated} updated, {events_created} created)."
        )
        self._logger.info("Finished updating transport notices.")

    def update_event(self, sources, event: TransportEvent):
        lines = []
        for line_str in event.lines:
            line, _ = app_models.TransportLine.objects.get_or_create(title=line_str)
            lines.append(line)

        obj, created = app_models.TransportItem.objects.update_or_create(
            source=sources[event.source_name],
            source_identifier=event.source_id,
            defaults={
                "title": event.title,
                "body": event.description,
                "start_date": event.event_start,
                "stop_date": event.event_stop,
                "is_train": self._get_tag_values(event.tags, "IsTrain") == "Yes",
                "view_url": self._get_tag_values(event.tags, "Link"),
                "notice_type": self._get_tag_values(event.tags, "EventType"),
                "category": self._get_tag_values(event.tags, "Category"),
                "severity": self._get_tag_values(event.tags, "Severity"),
                "timing": self._get_tag_values(event.tags, "When"),
                "location": self._get_tag_values(event.tags, "Locations"),
            },
        )
        obj.lines.set(lines)
        return obj, created

    def get_events(self, tl, qr, threshold_date: datetime):
        for event in tl.fetch():
            if self.keep(event, threshold_date):
                yield event

        for event in qr.fetch():
            if self.keep(event, threshold_date):
                yield event

    def keep(
        self, event: TransportEvent, threshold_date: datetime
    ) -> Optional[TransportEvent]:
        """Remove events without dates or ended before threshold date."""
        has_start = event.event_start is not None
        has_stop = event.event_stop is not None
        if not has_start and not has_stop:
            # ignore events with no dates
            return None

        elif has_stop and event.event_stop < threshold_date:
            # ignore events where the stop is before the filter date
            return None

        # include events where start date is before filter date
        # as some events have only start dates (continuing events)
        return event

    def _tidy(self, event: TransportEvent):
        is_train = False
        for index, line in enumerate(event.lines):
            line_str = str(line)
            if line_str.endswith(" Line"):
                line_str = line_str[0:-5]
                event.lines[index] = line_str
            line_str = slugify(line_str)
            if line_str in self.train_lines:
                is_train = True

        if is_train:
            event.tags.append(("IsTrain", "Yes"))

    def _get_tag_values(self, tags: list[tuple[str, str]], key: str):
        value = ", ".join(sorted(set([v for k, v in tags if k == key])))
        return value

    def create_au_qld_translink(self):

        (obj, created) = app_models.InformationSource.objects.get_or_create(
            name=TranslinkNotices.code,
            defaults={
                "title": TranslinkNotices.title,
                "info_url": TranslinkNotices.page_url,
            },
        )
        return obj, created

    def create_au_qld_rail(self):
        obj, created = app_models.InformationSource.objects.get_or_create(
            name=QldRailEvents.code,
            defaults={
                "title": QldRailEvents.title,
                "info_url": QldRailEvents.page_url,
            },
        )
        return obj, created
