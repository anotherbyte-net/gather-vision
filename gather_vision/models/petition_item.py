from django.db import models

from gather_vision.models.petition_source import PetitionSource


class PetitionItem(models.Model):
    """A petition to a governing body."""

    source = models.ForeignKey(
        PetitionSource,
        related_name="petitions",
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        max_length=1000,
        help_text="The title of the petition.",
    )
    code = models.CharField(
        max_length=50,
        help_text="The petition reference code.",
    )
    view_url = models.URLField(
        help_text="The url to the petition.",
    )
    principal = models.CharField(
        max_length=300,
        help_text="The name (and address) of the principal petitioner.",
    )
    sponsor = models.CharField(
        max_length=100,
        help_text="The name of the sponsor of the petition.",
    )
    eligibility = models.CharField(
        max_length=100,
        help_text="The eligibility to sign the petition.",
    )
    body = models.TextField(
        help_text="The text of the petition.",
    )
    opened_date = models.DateField(
        blank=True,
        null=True,
        help_text="The date this petition opened.",
    )
    closed_date = models.DateField(
        help_text="The date this petition closed.",
    )

    class Meta:
        pass

    constraints = [
        models.UniqueConstraint(
            fields=["source", "code"],
            name="petition_item_unique_source_code",
        )
    ]

    def __str__(self):
        return f'Started {self.opened_date}: "{self.title}"'
