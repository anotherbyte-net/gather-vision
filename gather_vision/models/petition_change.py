from django.db import models
from django.db.models import Min, Max

from gather_vision.models.petition_item import PetitionItem

from gather_vision.models.abstract_base import AbstractBase


class PetitionChange(AbstractBase):
    """A change in the number of signatures for a petition."""

    petition = models.ForeignKey(
        PetitionItem,
        on_delete=models.CASCADE,
        related_name="signature_changes",
        help_text="The petition.",
    )
    retrieved_date = models.DateTimeField(
        help_text="The date this petition update was retrieved.",
    )
    signatures = models.PositiveIntegerField(
        help_text="The number of signatures.",
    )

    class Meta:
        ordering = ["retrieved_date"]

    def __str__(self):
        return f"{self.signatures} total signatures by {self.retrieved_date}"

    @classmethod
    def get_retrieved_date_range(cls):
        query = cls.objects.aggregate(Max("retrieved_date"), Min("retrieved_date"))
        return {
            "min": query.get("retrieved_date__min"),
            "max": query.get("retrieved_date__max"),
        }
