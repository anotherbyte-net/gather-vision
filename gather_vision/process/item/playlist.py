from dataclasses import dataclass, field
from typing import Iterable

from gather_vision.process.item.track import Track


@dataclass(frozen=True)
class Playlist:

    name: str
    title: str

    tracks: list[Track] = field(default_factory=list, repr=False, compare=False)

    def add_track(
        self,
        service_name: str,
        collection_name: str,
        track_number: int,
        track_id: str,
        title: str,
        primary_artists: Iterable[str],
        featured_artists: Iterable[str],
        queries: Iterable[str],
        raw: dict,
    ) -> None:
        self.tracks.append(
            Track(
                service_name=service_name,
                collection_name=collection_name,
                track_number=track_number,
                track_id=track_id,
                title=title,
                primary_artists=list(primary_artists),
                featured_artists=list(featured_artists),
                queries=list(queries),
                raw=raw,
            )
        )

    def __str__(self):
        return f"{self.title} ({self.name}) with {len(self.tracks)} tracks"
