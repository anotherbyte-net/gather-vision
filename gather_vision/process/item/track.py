from dataclasses import dataclass


@dataclass(frozen=True)
class Track:
    service_name: str
    collection_name: str
    track_number: int
    track_id: str
    title: str
    primary_artists: list[str]
    featured_artists: list[str]
    queries: list[str]
    raw: dict

    def __str__(self):
        return ":".join(
            [
                self.service_name,
                self.collection_name,
                str(self.track_number),
                ", ".join(self.primary_artists),
                self.title,
            ]
        )
