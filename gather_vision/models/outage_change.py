from django.db import models

from gather_vision.models import OutageItem
from gather_vision.models.abstract_base import AbstractBase


class OutageChange(AbstractBase):
    """A change in the number of customers for an outage."""

    outage = models.ForeignKey(
        OutageItem,
        models.CASCADE,
        related_name="customer_changes",
        help_text="The outage.",
    )
    customers = models.PositiveIntegerField(
        help_text="The number of customers affected.",
    )
    retrieved_date = models.DateTimeField(
        help_text="The date this outage update was retrieved.",
    )

    def __str__(self):
        return f"{self.customers} customers affected on {self.retrieved_date}"
