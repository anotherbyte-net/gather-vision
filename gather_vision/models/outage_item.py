from django.db import models

from gather_vision.models.abstract_base import AbstractBase
from gather_vision.models.information_source import InformationSource


class OutageItem(AbstractBase):
    """An electricity outage."""

    source = models.ForeignKey(
        InformationSource,
        related_name="outages",
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        "OutageGroup",
        related_name="outages",
        on_delete=models.CASCADE,
    )
    event_name = models.CharField(
        blank=True,
        max_length=500,
        help_text="The name of the outage event.",
    )
    council = models.CharField(
        max_length=500,
        help_text="The name of the council that covers the outage location.",
    )
    suburb = models.CharField(
        max_length=500,
        help_text="The name of the suburb that covers the outage location.",
    )
    post_code = models.CharField(
        blank=True,
        max_length=4,
        help_text="The location post code.",
    )
    cause = models.CharField(
        max_length=500,
        help_text="The cause of the outage.",
    )
    streets = models.CharField(
        blank=True,
        max_length=400,
        help_text="The name of the streets involved in the outage.",
    )
    restored_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date this outage ended.",
    )
    customers = models.PositiveIntegerField(
        help_text="The number of customers affected.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["group", "event_name"],
                name="outage_item_unique_group_event_name",
            )
        ]

    def __str__(self):
        return (
            f"{self.event_name} "
            f"caused by {self.cause} "
            f"restored on {self.restored_date}"
        )
