from django.db import models

from gather_vision.models.abstract_base import AbstractBase


class OutageGroup(AbstractBase):
    """A group of outages."""

    retrieved_date = models.DateTimeField(
        help_text="The date this outage update was retrieved.",
    )
    source_updated_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date the outage info was last updated by the source.",
    )
    demand = models.PositiveIntegerField(
        help_text="The amount of demand.",
    )
    rating = models.PositiveIntegerField(
        help_text="The rating of the demand level.",
    )
    total_customers = models.PositiveIntegerField(
        help_text="The total number of customers affected.",
    )

    def __str__(self):
        date = self.retrieved_date.date() if self.retrieved_date else None
        msg = f"{self.total_customers} customers"
        if date:
            msg += f" affected on {date}"
        return msg
