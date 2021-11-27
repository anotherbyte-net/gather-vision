from django.db import models

from gather_vision.models.petition_item import PetitionItem

from gather_vision.models.abstract_base import AbstractBase


class PetitionChange(AbstractBase):
    """A change in the number of signatures for a petition."""

    petition = models.ForeignKey(
        PetitionItem,
        models.CASCADE,
        related_name="signature_changes",
        help_text="The petition.",
    )
    retrieved_date = models.DateTimeField(
        help_text="The date this petition update was retrieved.",
    )
    signatures = models.PositiveIntegerField(
        help_text="The number of signatures.",
    )

    def __str__(self):
        return f"{self.signatures} aggregate signatures by {self.retrieved_date}"
