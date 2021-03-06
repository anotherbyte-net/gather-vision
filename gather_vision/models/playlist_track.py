from django.db import models

from gather_vision.models import InformationSource
from gather_vision.models.abstract_base import AbstractBase


class PlaylistTrack(AbstractBase):
    """A music track."""

    source = models.ForeignKey(
        InformationSource,
        related_name="tracks",
        on_delete=models.CASCADE,
        help_text="The source for this track information.",
    )
    code = models.CharField(
        max_length=100,
        help_text="The unique code assigned to this track by the music source.",
    )
    title = models.CharField(
        max_length=500,
        help_text="The title of the track.",
    )
    artists = models.CharField(
        max_length=800,
        help_text="The artists for the track.",
    )
    info_url = models.URLField(
        blank=True,
        help_text="A link to the information provided by the source about the track.",
    )
    image_url = models.URLField(
        blank=True,
        help_text="A link to the art for the track cover.",
    )
    musicbrainz_code = models.UUIDField(
        blank=True,
        null=True,
        help_text="The MusicBrainz recording id for this track.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "code"], name="music_track_unique_source_code"
            )
        ]

    def __str__(self):
        return f"{self.title} - {self.artists} ({self.code})"
