from django.db import models

from gather_vision.models.abstract_base import AbstractBase


class TransportLine(AbstractBase):
    """A transport network line name."""

    title = models.CharField(
        max_length=100,
        help_text="The displayed title of the transport network line.",
    )

    def __str__(self):
        return self.title
