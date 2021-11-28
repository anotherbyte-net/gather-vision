from django.db import models

from gather_vision.models import InformationSource
from gather_vision.models.abstract_base import AbstractBase


class TransportItem(AbstractBase):
    """A transport notice item."""

    source = models.ForeignKey(
        InformationSource,
        related_name="transport_items",
        on_delete=models.CASCADE,
    )
    lines = models.ManyToManyField(
        "TransportLine",
        related_name="notices",
        help_text="The lines involved in this transport notice.",
    )
    title = models.CharField(
        max_length=200,
        help_text="The title of the transport notice.",
    )
    body = models.TextField(
        help_text="The text of the transport notice.",
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text="The start date of this transport notice.",
    )
    stop_date = models.DateField(
        blank=True,
        null=True,
        help_text="The finish date this transport notice.",
    )
    is_train = models.BooleanField(
        # IsTrain
        help_text="Whether the transport notice includes train services.",
    )
    view_url = models.URLField(
        # Link
        blank=True,
        help_text="The url to view the transport notice.",
    )
    notice_type = models.CharField(
        # EventType
        blank=True,
        max_length=200,
        help_text="The type of the transport notice.",
    )
    category = models.CharField(
        # Category
        blank=True,
        max_length=200,
        help_text="The category of the transport notice.",
    )
    severity = models.CharField(
        # Severity
        blank=True,
        max_length=200,
        help_text="The severity of the transport notice.",
    )
    timing = models.CharField(
        # When
        blank=True,
        max_length=200,
        help_text="The timing of the transport notice.",
    )
    location = models.CharField(
        # Locations
        blank=True,
        max_length=500,
        help_text="The location covered by the transport notice.",
    )

    def __str__(self):
        result = [
            ("source", f"{self.source.name}-{self.source.id}"),
            ("title", self.title),
            ("start", self.start_date.isoformat() if self.start_date else ""),
            ("stop", self.stop_date.isoformat() if self.stop_date else ""),
            ("lines", ", ".join(self.lines or [])),
        ]
        return "; ".join(f"{k}={v}" for k, v in result)
