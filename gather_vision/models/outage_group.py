from django.db import models
from django.db.models import Max, Min

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

    @classmethod
    def get_retrieved_date_range(cls):
        query = cls.objects.aggregate(Max("retrieved_date"), Min("retrieved_date"))
        return {
            "min": query.get("retrieved_date__min"),
            "max": query.get("retrieved_date__max"),
        }

    @classmethod
    def get_items(cls, **kwargs):
        query = cls.objects.order_by("source_updated_date", "retrieved_date")
        if kwargs:
            query = query.filter(**kwargs)
        return query

    @classmethod
    def get_data_items(cls, start_date, stop_date):
        date_filters = {
            "retrieved_date__gte": start_date,
            "retrieved_date__lte": stop_date,
        }
        query = cls.get_items(**date_filters)
        return query
