from django.db import models as db_models


from gather_vision.apps.explore import models as explore_models
from gather_vision.obtain.core import models as core_models


class EventManager(db_models.Manager):
    def get_by_natural_key(self, name, origin):
        return self.get(name=name, origin=origin)


class Event(
    core_models.ChangedModelBase,
    core_models.NameTitleModelBase,
    core_models.DescriptionUrlModelBase,
    core_models.ModelBase,
):
    """An electricity network event."""

    origin = db_models.ForeignKey(
        explore_models.Origin,
        related_name="electricity_events",
        on_delete=db_models.CASCADE,
    )
    area = db_models.ForeignKey(
        explore_models.Area,
        related_name="electricity_event_areas",
        on_delete=db_models.PROTECT,
    )
    start_date = db_models.DateTimeField(
        blank=True,
        null=True,
        help_text="The date this event started.",
    )
    stop_date = db_models.DateField(
        blank=True,
        null=True,
        help_text="The date this event stopped.",
    )
    locations = db_models.CharField(
        blank=True,
        max_length=600,
        help_text="The name of the locations and streets involved in the event.",
    )

    objects = EventManager()

    class Meta:
        constraints = [
            db_models.UniqueConstraint(
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


class ProgressManager(db_models.Manager):
    def get_by_natural_key(self, occurred_date, event):
        return self.get(occurred_date=occurred_date, event=event)


class Progress(
    core_models.ChangedModelBase,
    core_models.RetrievedModelBase,
    core_models.IssuedOccurredModelBase,
    core_models.ModelBase,
):
    """Information about an event at a point in time."""

    event = db_models.ForeignKey(
        Event,
        related_name="progression",
        on_delete=db_models.CASCADE,
    )
    affected = db_models.PositiveIntegerField(
        help_text="The number of customers or other entities affected by the event.",
    )

    objects = ProgressManager()

    class Meta:
        constraints = [
            db_models.UniqueConstraint(
                fields=["occurred_date", "event"],
                name="electricity_progress_unique_occurred_date_event",
            )
        ]

    def natural_key(self):
        return (self.occurred_date,) + self.event.natural_key()

    natural_key.dependencies = ["electricity.event"]

    def __str__(self):
        return f"affects {self.affected} at {self.occurred_date}"


class UsageManager(db_models.Manager):
    def get_by_natural_key(self, occurred_date, origin):
        return self.get(occurred_date=occurred_date, origin=origin)


class Usage(
    core_models.ChangedModelBase,
    core_models.RetrievedModelBase,
    core_models.IssuedOccurredModelBase,
    core_models.ModelBase,
):
    """Information about electricity usage at a point in time."""

    # usage: id, origin_id, created_date, modified_date, issued_date, retrieved_date, demand, rating, affected (pos int)
    origin = db_models.ForeignKey(
        explore_models.Origin,
        related_name="electricity_usages",
        on_delete=db_models.CASCADE,
    )
    demand = db_models.PositiveIntegerField(
        help_text="The measure of electricity demand in megawatts.",
    )
    rating = db_models.PositiveIntegerField(
        help_text="The rating of the demand level.",
    )
    customers = db_models.PositiveIntegerField(
        help_text="The number of customers or other entities causing the demand.",
    )

    objects = ProgressManager()

    class Meta:
        constraints = [
            db_models.UniqueConstraint(
                fields=["occurred_date", "origin"],
                name="electricity_usage_unique_issued_date_origin",
            )
        ]

    def natural_key(self):
        return (self.occurred_date,) + self.origin.natural_key()

    natural_key.dependencies = ["explore.origin"]

    def __str__(self):
        return f"{self.customers} customers at {self.occurred_date} with demand {self.demand}MW"
