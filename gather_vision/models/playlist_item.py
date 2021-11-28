from django.db import models


from gather_vision.models import InformationSource
from gather_vision.models.abstract_base import AbstractBase


class PlaylistItem(AbstractBase):
    """An ordered collection of playlist entries."""

    source = models.ForeignKey(
        InformationSource,
        related_name="playlists",
        on_delete=models.CASCADE,
    )
    retrieved_date = models.DateTimeField(
        help_text="The date and time this playlist was retrieved.",
    )
