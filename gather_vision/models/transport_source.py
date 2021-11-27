from django.db import models

from gather_vision.models.abstract_base import AbstractBase


class TransportSource(AbstractBase):
    """A source that provides transport notices."""

    name = models.SlugField(
        unique=True,
        help_text="The name of the transport notices source.",
    )
    title = models.CharField(
        max_length=100,
        help_text="The displayed title of the transport notices source.",
    )
    info_url = models.URLField(
        blank=True,
        help_text="A link to information about the transport notices source.",
    )

    def __str__(self):
        return f'{self.name}: "{self.title}"'
