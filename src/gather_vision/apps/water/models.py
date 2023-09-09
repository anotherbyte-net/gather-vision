from django.db import models

from gather_vision.apps.explore.models import Origin, Coordinate, Area
from gather_vision.obtain.core import base


class StationManager(models.Manager):
    def get_by_natural_key(self, name, origin):
        return self.get(name=name, origin=origin)


class Station(
    base.ModelChangedMixin,
    base.ModelNameTitleMixin,
    base.ModelDescriptionUrlMixin,
    base.ModelBase,
):
    """A water measurement station."""

    origin = models.ForeignKey(
        Origin,
        related_name="water_stations",
        on_delete=models.CASCADE,
    )
    area = models.ForeignKey(
        Area,
        blank=True,
        null=True,
        related_name="water_stations",
        on_delete=models.PROTECT,
    )
    coordinate = models.ForeignKey(
        Coordinate,
        blank=True,
        null=True,
        related_name="water_stations",
        on_delete=models.PROTECT,
    )

    objects = StationManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["origin", "name"],
                name="water_station_unique_origin_name",
            )
        ]

    def natural_key(self):
        return (self.name,) + self.origin.natural_key()

    natural_key.dependencies = ["explore.origin"]

    def __str__(self):
        return f"water station {self.title} ({self.name})"


class GroupManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Group(
    base.ModelChangedMixin,
    base.ModelNameTitleMixin,
    base.ModelBase,
):
    """A named collection of measurements."""

    objects = GroupManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="water_group_unique_name",
            )
        ]

    def natural_key(self):
        return (self.name,)

    natural_key.dependencies = []

    def __str__(self):
        return f"group {self.title} ({self.name})"


class MeasureManager(models.Manager):
    def get_by_natural_key(self, issued_date, station):
        return self.get(issued_date=issued_date, station=station)


class Measure(
    base.ModelChangedMixin,
    base.ModelRetrievedMixin,
    base.ModelIssuedOccurredMixin,
    base.ModelBase,
):
    """A measure at a station."""

    CATEGORY_OBSERVED_HEIGHT = "observed_height"
    CATEGORY_OBTAINED_SAMPLE = "obtained_sample"
    CATEGORY_FORECAST_HEIGHT = "forecast_height"
    CATEGORY_THRESHOLD = "threshold"
    CATEGORY_CHOICES = [
        (CATEGORY_OBSERVED_HEIGHT, "Observed height"),
        (CATEGORY_OBTAINED_SAMPLE, "Obtained sample"),
        (CATEGORY_FORECAST_HEIGHT, "Forecast height"),
        (CATEGORY_THRESHOLD, "Threshold"),
    ]

    QUALITY_VALID = "valid"
    QUALITY_INVALID = "invalid"
    QUALITY_NOT_TESTED = "not_tested"
    QUALITY_WARN_MINOR = "warn_minor"
    QUALITY_WARN_MODERATE = "warn_moderate"
    QUALITY_WARN_MAJOR = "warn_major"
    QUALITY_CHOICES = [
        (QUALITY_VALID, "Valid"),
        (QUALITY_INVALID, "Invalid"),
        (QUALITY_NOT_TESTED, "Not tested"),
        (QUALITY_WARN_MINOR, "Minor warning"),
        (QUALITY_WARN_MODERATE, "Moderate warning"),
        (QUALITY_WARN_MAJOR, "Major warning"),
    ]

    station = models.ForeignKey(
        Station,
        related_name="measurements",
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        related_name="measurements",
        on_delete=models.PROTECT,
    )
    level = models.FloatField(
        blank=True,
        null=True,
        help_text="The value of the measurement.",
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="The measure type.",
    )
    quality = models.CharField(
        max_length=20,
        choices=QUALITY_CHOICES,
        help_text="The measure quality or status.",
    )

    objects = MeasureManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["occurred_date", "station"],
                name="water_measure_unique_occurred_date_station",
            )
        ]

    def natural_key(self):
        return (self.occurred_date,) + self.station.natural_key()

    natural_key.dependencies = ["water.station"]

    def __str__(self):
        return (
            f"measure {self.level} at {self.occurred_date} "
            f"({self.get_category_display()} - {self.get_quality_display()})"
        )
