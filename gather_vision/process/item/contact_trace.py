from dataclasses import dataclass
from datetime import datetime


@dataclass
class ContactTrace:
    start_datetime: datetime
    stop_datetime: datetime
    added_datetime: datetime
    retrieved_datetime: datetime

    category: str
    lgas: str
    suburb: str
    location: str
    address: str

    @classmethod
    def csv_headers(cls):
        return [
            "start_datetime",
            "stop_datetime",
            "added_datetime",
            "retrieved_datetime",
            "lgas",
            "suburb",
            "location",
            "address",
        ]

    def csv_row(self):
        return {
            "start_datetime": self._format_datetime(self.start_datetime),
            "stop_datetime": self._format_datetime(self.stop_datetime),
            "added_datetime": self._format_datetime(self.added_datetime),
            "retrieved_datetime": self._format_datetime(self.retrieved_datetime),
            "lgas": self.lgas,
            "suburb": self.suburb,
            "location": self.location,
            "address": self.address,
        }

    def display_text(self):
        return ""

    def compare(self, other: "ContactTrace"):
        return all(
            [
                self.start_datetime == other.start_datetime,
                self.stop_datetime == other.stop_datetime,
                self.added_datetime == other.added_datetime,
                self.retrieved_datetime == other.retrieved_datetime,
                self.category == other.category,
                self.lgas == other.lgas,
                self.suburb == other.suburb,
                self.location == other.location,
                self.address == other.address,
            ]
        )

    def _format_datetime(self, value: datetime):
        return value.isoformat(timespec="seconds")
