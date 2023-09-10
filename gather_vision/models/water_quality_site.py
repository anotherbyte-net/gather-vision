from django.db import models

import gather_vision.obtain.core.models


class WaterQualitySite(
    gather_vision.obtain.core.models.DescriptionUrlModelBase,
    gather_vision.obtain.core.models.DescriptionUrlModelBase,
    gather_vision.obtain.core.models.NameTitleModelBase,
    AbstractBase,
):
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
