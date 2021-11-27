from django.db import models


class PlaylistSource(models.Model):
    """A source that provides lists of music tracks."""

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="The name of the playlist source.",
    )
    title = models.CharField(
        max_length=100,
        help_text="The displayed title of the playlist source.",
    )
    info_url = models.URLField(
        blank=True,
        help_text="A link to information about the playlist source.",
    )
