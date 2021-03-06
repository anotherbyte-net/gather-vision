from django.db import models

from gather_vision.models import AbstractBase, InformationSource


class PetitionItem(AbstractBase):
    """A petition to a governing body."""

    source = models.ForeignKey(
        InformationSource,
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
        blank=True,
        max_length=100,
        help_text="The name of the sponsor of the petition.",
    )
    eligibility = models.CharField(
        blank=True,
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
        constraints = [
            models.UniqueConstraint(
                fields=["source", "code"],
                name="petition_item_unique_source_code",
            )
        ]

    def __str__(self):
        return f'Started {self.opened_date}: "{self.title}"'

    @classmethod
    def get_items(cls, **kwargs):
        query = cls.objects.order_by("opened_date", "closed_date", "code")
        if kwargs:
            query = query.filter(**kwargs)
        query = query.prefetch_related("source", "signature_changes")
        return query

    @classmethod
    def get_data_items(cls, start_date, stop_date):
        date_filters = {
            "signature_changes__retrieved_date__gte": start_date,
            "signature_changes__retrieved_date__lte": stop_date,
        }
        query = cls.get_items(**date_filters)
        return query
