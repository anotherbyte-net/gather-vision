from django.db import models

from gather_vision.models.abstract_base import AbstractBase
from gather_vision.models.information_source import InformationSource


class WaterQualitySite(AbstractBase):
    """A location used to obtain water quality samples."""

    source = models.ForeignKey(
        InformationSource,
        related_name="water_quality_sites",
        on_delete=models.CASCADE,
    )
    code = models.CharField(
        max_length=10,
        help_text="The site reference code.",
    )
    title = models.CharField(
        max_length=100,
        help_text="The title of the site.",
    )
    description = models.TextField(
        help_text="The description of the site.",
    )
    latitude = models.DecimalField(
        max_digits=7,
        decimal_places=5,
        help_text="The latitude or North/South position.",
    )
    longitude = models.DecimalField(
        max_digits=8,
        decimal_places=5,
        help_text="The longitude or East/West position.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "code"],
                name="water_quality_site_unique_source_code",
            )
        ]

    def __str__(self):
        return f"{self.title} at {self.latitude}°, {self.longitude}°"
