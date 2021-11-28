from django.db import models

from gather_vision.models import PlaylistTrack
from gather_vision.models import PlaylistItem
from gather_vision.models.abstract_base import AbstractBase


class PlaylistEntry(AbstractBase):
    """An entry in a playlist that is linked to a number of tracks."""

    playlist = models.ForeignKey(
        PlaylistItem,
        models.CASCADE,
        related_name="entries",
        help_text="The playlist that contains this entry.",
    )
    tracks = models.ManyToManyField(
        PlaylistTrack,
        related_name="entries",
        help_text="The tracks that match this playlist entry.",
    )
    position_change = models.IntegerField(
        blank=True,
        null=True,
        help_text="The position change of this entry "
        "compared to the previously generated playlist.",
    )
    order = models.PositiveIntegerField(
        help_text="The order of this entry in the playlist.",
    )

    class Meta:
        verbose_name_plural = "Playlist entries"
        constraints = [
            models.UniqueConstraint(
                fields=["playlist", "order"],
                name="playlist_entry_unique_playlist_order",
            )
        ]
