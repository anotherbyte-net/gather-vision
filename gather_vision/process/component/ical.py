from datetime import datetime
from typing import Optional

import icalendar as cal


class ICal:
    """Create and specify an iCalendar with events."""

    def __init__(self, provider: str, title: str, description: str, tz: str, ttl: str):
        c = cal.Calendar()
        c.add("prodid", f"-//{title}//{provider}//EN")
        c.add("version", "2.0")
        c.add("calscale", "GREGORIAN")
        c.add("method", "PUBLISH")
        c.add("X-WR-CALNAME", title)
        c.add("X-WR-CALDESC", description)
        c.add("X-WR-TIMEZONE", tz)
        c.add("X-PUBLISHED-TTL", ttl)

        self._c = c

    def get_calendar(self):
        return self._c

    def add_event(
        self,
        title: str,
        body: str,
        date_start: datetime,
        date_stop: datetime,
        location: Optional[str] = None,
        url: Optional[str] = None,
        event_class: str = "PUBLIC",
        uid: Optional[str] = None,
        date_stamp: Optional[datetime] = None,
        date_modified: Optional[datetime] = None,
        date_created: Optional[datetime] = None,
        sequence_num: Optional[int] = None,
    ):
        """Add a new event to the calendar."""

        # vevent:
        # https://datatracker.ietf.org/doc/html/rfc5545#section-3.6.1
        e = cal.Event()
        e.add("summary", title)
        e.add("description", body)

        # dtstart:
        # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.2.4
        e.add("dtstart", date_start)

        # dtend:
        # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.2.2
        e.add("dtend", date_stop)

        if location:
            e.add("location", location)

        if url:
            e.add("url", location)

        if event_class:
            e.add("class", event_class)

        if uid:
            # uid: (persistent, globally unique identifier)
            e.add("uid", uid)

        if date_stamp:
            # dtstamp:
            # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.7.2
            e.add("dtstamp", date_stamp)

        if date_modified:
            # last-modified:
            # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.7.3
            e.add("last-modified", date_modified)

        if date_created:
            # created:
            # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.7.1
            e.add("created", date_created)

        if sequence_num is not None:
            # sequence:
            # https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.7.4
            e.add("sequence", sequence_num)

        self._c.add_component(e)
