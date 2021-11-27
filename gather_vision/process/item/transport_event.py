from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TransportEvent:
    raw: dict

    title: str
    description: str

    tags: list[tuple[str, str]]

    lines: list[str]

    source_id: str
    source_name: str

    event_start: datetime
    event_stop: datetime

    @property
    def sort_str(self):
        return "-".join(
            [
                str(self.event_start) if self.event_start else "",
                str(self.event_stop) if self.event_stop else "",
            ]
        )

    @classmethod
    def cvs_headers(cls):
        return [
            "source_name",
            "source_id",
            "title",
            "description",
            "event_start",
            "event_stop",
            "lines",
            "tags",
        ]

    @property
    def csv_row(self):
        return {
            "source_name": self.source_name,
            "source_id": self.source_id,
            "title": self.title,
            "description": self.description,
            "event_start": self.event_start.isoformat() if self.event_start else "",
            "event_stop": self.event_stop.isoformat() if self.event_stop else "",
            "lines": ";".join(sorted(self.lines)),
            "tags": ";".join(sorted([f"{k}={v}" for k, v in self.tags])),
        }

    def __str__(self):
        result = [
            ("source", f"{self.source_name}-{self.source_id}"),
            ("title", self.title),
            ("start", self.event_start.isoformat() if self.event_start else ""),
            ("stop", self.event_stop.isoformat() if self.event_stop else ""),
            ("lines", ", ".join(self.lines or [])),
        ]
        return "; ".join(f"{k}={v}" for k, v in result)
