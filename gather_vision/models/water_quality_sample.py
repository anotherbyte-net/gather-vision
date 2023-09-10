from django.db import models

from gather_vision.models.abstract_base import AbstractBase
from gather_vision.models.water_quality_site import WaterQualitySite

import gather_vision.obtain.core.models


class WaterQualitySample(
    gather_vision.obtain.core.models.RetrievedModelBase, AbstractBase
):
    """A water quality sample obtained from a site."""

    VALID = "valid"
    INVALID = "invalid"
    NOT_TESTED = "not_tested"

    SAMPLES_STATUSES = [
        (VALID, "Valid"),
        (INVALID, "Invalid"),
        (NOT_TESTED, "Not tested"),
    ]

    site = models.ForeignKey(
        WaterQualitySite,
        on_delete=models.CASCADE,
        related_name="samples",
        help_text="The sample site.",
    )
    sample_date = models.DateField(
        help_text="The date this sample was conducted.",
    )
    sample_value = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="The value of the sample.",
    )
    sample_status = models.CharField(
        blank=False,
        null=False,
        max_length=20,
        choices=SAMPLES_STATUSES,
        default=NOT_TESTED,
        help_text="The status of the sample.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["site", "sample_date"],
                name="water_quality_sample_unique_site_date",
            )
        ]

    def __str__(self):
        if self.sample_value is not None:
            value = str(self.sample_value)
        else:
            value = self.sample_status

        return f"{value} on {self.sample_date}"
