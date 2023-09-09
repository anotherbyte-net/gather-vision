from django.db import models

from gather_vision.apps.explore.models import Origin, Area
from gather_vision.obtain.core import base


class EventManager(models.Manager):
    def get_by_natural_key(self, name, origin):
        return self.get(name=name, origin=origin)


class Event(
    base.ModelChangedMixin,
    base.ModelNameTitleMixin,
    base.ModelDescriptionUrlMixin,
    base.ModelBase,
):
    """An electricity network event."""

    origin = models.ForeignKey(
        Origin,
        related_name="electricity_events",
        on_delete=models.CASCADE,
    )
    area = models.ForeignKey(
        Area,
        related_name="electricity_event_areas",
        on_delete=models.PROTECT,
    )
    start_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="The date this event started.",
    )
    stop_date = models.DateField(
        blank=True,
        null=True,
        help_text="The date this event stopped.",
    )
    locations = models.CharField(
        blank=True,
        max_length=600,
        help_text="The name of the locations and streets involved in the event.",
    )

    objects = EventManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "origin"],
                name="electricity_event_unique_name_origin",
            )
        ]

    def natural_key(self):
        return (self.name,) + self.origin.natural_key()

    natural_key.dependencies = ["explore.origin"]

    def __str__(self):
        if self.start_date:
            return f"{self.title} started on {self.start_date}"
        if self.stop_date:
            return f"{self.title} ended on {self.stop_date}"
        return self.title


class ProgressManager(models.Manager):
    def get_by_natural_key(self, occurred_date, event):
        return self.get(occurred_date=occurred_date, event=event)


class Progress(
    base.ModelChangedMixin,
    base.ModelRetrievedMixin,
    base.ModelIssuedOccurredMixin,
    base.ModelBase,
):
    """Information about an event at a point in time."""

    event = models.ForeignKey(
        Event,
        related_name="progression",
        on_delete=models.CASCADE,
    )
    affected = models.PositiveIntegerField(
        help_text="The number of customers or other entities affected by the event.",
    )

    objects = ProgressManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["occurred_date", "event"],
                name="electricity_progress_unique_occurred_date_event",
            )
        ]

    def natural_key(self):
        return (self.occurred_date,) + self.event.natural_key()

    natural_key.dependencies = ["electricity.event"]

    def __str__(self):
        return f"affects {self.affected} at {self.occurred_date}"


class UsageManager(models.Manager):
    def get_by_natural_key(self, occurred_date, origin):
        return self.get(occurred_date=occurred_date, origin=origin)


class Usage(
    base.ModelChangedMixin,
    base.ModelRetrievedMixin,
    base.ModelIssuedOccurredMixin,
    base.ModelBase,
):
    """Information about electricity usage at a point in time."""

    # usage: id, origin_id, created_date, modified_date, issued_date, retrieved_date, demand, rating, affected (pos int)
    origin = models.ForeignKey(
        Origin,
        related_name="electricity_usages",
        on_delete=models.CASCADE,
    )
    demand = models.PositiveIntegerField(
        help_text="The measure of electricity demand in megawatts.",
    )
    rating = models.PositiveIntegerField(
        help_text="The rating of the demand level.",
    )
    customers = models.PositiveIntegerField(
        help_text="The number of customers or other entities causing the demand.",
    )

    objects = ProgressManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["occurred_date", "origin"],
                name="electricity_usage_unique_issued_date_origin",
            )
        ]

    def natural_key(self):
        return (self.occurred_date,) + self.origin.natural_key()

    natural_key.dependencies = ["explore.origin"]

    def __str__(self):
        return f"{self.customers} customers at {self.occurred_date} with demand {self.demand}MW"
