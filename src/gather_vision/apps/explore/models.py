from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

from gather_vision.obtain.core import base


class CustomUser(AbstractUser):
    pass


class CoordinateManager(models.Manager):
    def get_by_natural_key(self, latitude, longitude, reference_system):
        return self.get(
            latitude=latitude, longitude=longitude, reference_system=reference_system
        )


class Coordinate(
    base.ModelChangedMixin,
    base.ModelBase,
):
    """A geographic coordinate."""

    latitude = models.DecimalField(
        max_digits=7,
        decimal_places=5,
        help_text="The latitude (North/South position, -90 to +90).",
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=8,
        decimal_places=5,
        help_text="The longitude (East/West position -180 to +180).",
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    reference_system = models.SlugField(
        blank=True,
        help_text="The geographic spatial reference system for the coordinates.",
    )

    objects = CoordinateManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["latitude", "longitude", "reference_system"],
                name="explore_coordinate_unique_latitude_longitude_ref",
            )
        ]

    def natural_key(self):
        return self.latitude, self.longitude, self.reference_system

    natural_key.dependencies = []

    def __str__(self):
        return f"{self.latitude},{self.longitude} ({self.reference_system})"


class AreaManager(models.Manager):
    def get_by_natural_key(self, name, level, parent):
        return self.get(name=name, level=level, parent=parent)


class Area(
    base.ModelChangedMixin,
    base.ModelNameTitleMixin,
    base.ModelBase,
):
    """A known geographical location."""

    # region = administrative division / state / province
    # district = county / sub-administrative division
    # locality = city / town
    # neighbourhood = suburb / dependent locality

    LEVEL_COUNTRY = "L1"
    LEVEL_REGION = "L2"
    LEVEL_DISTRICT = "L3"
    LEVEL_LOCALITY = "L4"
    LEVEL_NEIGHBOURHOOD = "L5"
    LEVEL_CHOICES = [
        (LEVEL_COUNTRY, "Country (level 1)"),
        (LEVEL_REGION, "Region (level 2)"),
        (LEVEL_DISTRICT, "District (level 3)"),
        (LEVEL_LOCALITY, "Locality (level 4)"),
        (LEVEL_NEIGHBOURHOOD, "Neighbourhood (level 5)"),
    ]

    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="The parent area that contains this area.",
    )
    level = models.CharField(
        max_length=2,
        choices=LEVEL_CHOICES,
        help_text="The division level.",
    )

    objects = AreaManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "level", "parent"],
                name="explore_area_unique_name_level_parent",
            )
        ]

    def natural_key(self):
        return self.name, self.level, self.parent

    natural_key.dependencies = ["explore.area"]

    def __str__(self):
        return f"{self.title} ({self.name},{self.get_level_display()})"


class OriginManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Origin(
    base.ModelChangedMixin,
    base.ModelNameTitleMixin,
    base.ModelDescriptionUrlMixin,
    base.ModelBase,
):
    """"""

    area = models.ForeignKey(
        Area,
        blank=True,
        null=True,
        related_name="origins",
        on_delete=models.PROTECT,
    )

    objects = OriginManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="explore_area_unique_name",
            )
        ]

    def natural_key(self):
        return (self.name,)

    natural_key.dependencies = []

    def __str__(self):
        return f"{self.title} ({self.name})"
