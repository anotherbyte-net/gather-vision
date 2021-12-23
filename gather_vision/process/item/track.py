from dataclasses import dataclass

from django.utils.text import slugify


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

    def matches_model(self, model: "PlaylistTrack"):
        """Match this track to a playlist track model using service and id."""
        track_source_name = f"{self.service_name}_{self.collection_name}"
        return track_source_name == model.source.name and model.code == self.track_id

    def matches_track_title_artists(self, other: "Track"):
        """Match this track to another track using title and artists."""

        if slugify(self.title) != slugify(other.title):
            return False

        self_primary = sorted([slugify(i) for i in self.primary_artists])
        self_featured = sorted([slugify(i) for i in self.featured_artists])
        self_artists = sorted(self_primary + self_featured)

        other_primary = sorted([slugify(i) for i in other.primary_artists])
        other_featured = sorted([slugify(i) for i in other.featured_artists])
        other_artists = sorted(other_primary + other_featured)

        if self_primary == other_primary and self_featured == other_featured:
            return True

        if self_artists == other_artists:
            return True

        if all([i in self_artists for i in other_artists]):
            return True

        if all([i in other_artists for i in self_artists]):
            return True

        return False

    def matches_track_service(self, other: "Track"):
        """Match this track to another track using service and id."""
        return all(
            [
                self.service_name == other.service_name,
                self.collection_name == other.collection_name,
                self.track_id == other.track_id,
            ]
        )

    @property
    def iter_artists(self):
        artists = (self.primary_artists or []) + (self.featured_artists or [])
        for i in sorted(range(len(artists)), reverse=True):
            start_index = 0
            stop_index = i + 1
            yield artists[start_index:stop_index]

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

    def _compare_artists(self, a: list[str], b: list[str]):
        return sorted([slugify(i) for i in a]) == sorted([slugify(i) for i in b])
