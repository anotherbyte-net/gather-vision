from django.db import models

from gather_vision.models.abstract_base import AbstractBase


class PetitionSource(AbstractBase):
    """A source that provides information about petitions."""

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="The name of the petition source.",
    )
    title = models.CharField(
        max_length=100,
        help_text="The displayed title of the petition source.",
    )
    info_url = models.URLField(
        blank=True,
        help_text="A link to information about the petition source.",
    )

    def __str__(self):
        return f'{self.name}: "{self.title}"'
