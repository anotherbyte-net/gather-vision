from django.db import models

from gather_vision.models.abstract_base import AbstractBase


class InformationSource(AbstractBase):
    """A source that provides information."""

    name = models.SlugField(
        unique=True,
        help_text="The name of the information source.",
    )
    title = models.CharField(
        max_length=100,
        help_text="The displayed title.",
    )
    info_url = models.URLField(
        blank=True,
        help_text="A link to details about the information source.",
    )

    def __str__(self):
        return f'{self.name}: "{self.title}"'

    def long_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "info_url": self.info_url,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
        }

    def long_csv(self):
        return {
            "name": self.name,
            "title": self.title,
            "info_url": self.info_url,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
        }
