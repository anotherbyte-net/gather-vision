import typing

from asgiref.sync import sync_to_async
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models as db_models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

from gather_vision.obtain.core import models as core_models
from gather_vision.obtain.core.data import GatherDataArea


class CustomUser(AbstractUser):
    pass


class CoordinateManager(db_models.Manager):
    def get_by_natural_key(self, latitude, longitude, reference_system):
        return self.get(
            latitude=latitude, longitude=longitude, reference_system=reference_system
        )


class Coordinate(
    core_models.ChangedModelBase,
    core_models.ModelBase,
):
    """A geographic coordinate."""

    latitude = db_models.DecimalField(
        max_digits=7,
        decimal_places=5,
        help_text="The latitude (North/South position, -90 to +90).",
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = db_models.DecimalField(
        max_digits=8,
        decimal_places=5,
        help_text="The longitude (East/West position -180 to +180).",
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    reference_system = db_models.SlugField(
        blank=True,
        help_text="The geographic spatial reference system for the coordinates.",
    )

    objects = CoordinateManager()

    class Meta:
        constraints = [
            db_models.UniqueConstraint(
                fields=["latitude", "longitude", "reference_system"],
                name="explore_coordinate_unique_latitude_longitude_ref",
            )
        ]

    def natural_key(self):
        return self.latitude, self.longitude, self.reference_system

    natural_key.dependencies = []

    def __str__(self):
        return f"{self.latitude},{self.longitude} ({self.reference_system})"


class AreaManager(db_models.Manager):
    def get_by_natural_key(self, name, level, parent):
        return self.get(name=name, level=level, parent=parent)


class Area(
    core_models.ChangedModelBase,
    core_models.NameTitleModelBase,
    core_models.ModelBase,
):
    """A known geographical location."""

    LEVEL_COUNTRY = "L1"
    """administrative extent of a sovereign government"""

    LEVEL_REGION = "L2"
    """administrative division / state / province"""

    LEVEL_DISTRICT = "L3"
    """county / sub-administrative division / local government area / ABS SA4"""

    LEVEL_LOCALITY = "L4"
    """city / town / geographical extent of populated area / ABS SA3"""

    LEVEL_NEIGHBOURHOOD = "L5"
    """suburb / dependent locality / ABS SA2"""

    LEVEL_CHOICES = [
        (LEVEL_COUNTRY, "Country (level 1)"),
        (LEVEL_REGION, "Region (level 2)"),
        (LEVEL_DISTRICT, "District (level 3)"),
        (LEVEL_LOCALITY, "Locality (level 4)"),
        (LEVEL_NEIGHBOURHOOD, "Neighbourhood (level 5)"),
    ]

    parent = db_models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=db_models.CASCADE,
        help_text="The parent area that contains this area.",
    )
    level = db_models.CharField(
        max_length=2,
        choices=LEVEL_CHOICES,
        help_text="The division level.",
    )

    objects = AreaManager()

    class Meta:
        constraints = [
            db_models.UniqueConstraint(
                fields=["name", "level", "parent"],
                name="explore_area_unique_name_level_parent",
            )
        ]

    def natural_key(self):
        return self.name, self.level, self.parent

    natural_key.dependencies = ["explore.area"]

    def __str__(self):
        return f"{self.title} ({self.name},{self.get_level_display()})"

    def parent_valid(self, level: str) -> None:
        msg = "A %s may have only a %s as a parent."
        match self.level:
            case self.LEVEL_COUNTRY:
                raise ValueError("A country cannot have a parent.")
            case self.LEVEL_REGION:
                if level != self.LEVEL_COUNTRY:
                    raise ValueError(msg % ("region", "country"))
            case self.LEVEL_DISTRICT:
                if level != self.LEVEL_REGION:
                    raise ValueError(msg % ("district", "region"))
            case self.LEVEL_LOCALITY:
                if level != self.LEVEL_DISTRICT:
                    raise ValueError(msg % ("locality", "district"))
            case self.LEVEL_NEIGHBOURHOOD:
                if level != self.LEVEL_LOCALITY:
                    raise ValueError(msg % ("neighbourhood", "locality"))
            case _:
                raise ValueError(f"A {self.level} cannot have {level} as a parent.")

    @classmethod
    async def from_obtain_data(cls, values: typing.Iterable[GatherDataArea]) -> "Area":
        """Create the areas and return the 'most precise' area
        (the highest level number)."""
        # sort by level, as it is the first item of the tuple
        definitions = sorted(values)

        # check for duplicate levels
        seen = set()
        dupes = [d.level for d in definitions if d.level in seen or seen.add(d.level)]
        if dupes:
            msg = (
                f"Cannot have more than one level in definitions, "
                f"found multiple levels: {sorted(dupes)}"
            )
            raise ValueError(msg)

        # get or create each level,
        # then use the area as the parent of the next area
        current: Area | None = None
        for d in definitions:
            query = {"name": slugify(d.title), "level": d.level}
            defaults = {"title": d.title}
            new_obj = Area(**{**defaults, **query})

            if new_obj and current:
                new_obj.parent_valid(getattr(current, "level"))
                new_obj.parent = current

            await cls.do_validation(new_obj)
            current, created = await Area.objects.aget_or_create(
                **query, defaults=defaults
            )

        # return the last area, which is the 'most precise' area
        return current


class OriginManager(db_models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Origin(
    core_models.ChangedModelBase,
    core_models.NameTitleModelBase,
    core_models.DescriptionUrlModelBase,
    core_models.ModelBase,
):
    """A source of data."""

    area = db_models.ForeignKey(
        Area,
        blank=True,
        null=True,
        related_name="origins",
        on_delete=db_models.PROTECT,
    )

    objects = OriginManager()

    class Meta:
        constraints = [
            db_models.UniqueConstraint(
                fields=["name"],
                name="explore_area_unique_name",
            )
        ]

    def natural_key(self):
        return (self.name,)

    natural_key.dependencies = []

    def __str__(self):
        return f"{self.title} ({self.name})"

    @classmethod
    async def from_obtain_data(
        cls, title: str, description: str | None, url: str | None, area: Area | None
    ) -> "Origin":
        query = {"name": slugify(title)}
        defaults = {
            "title": title,
            "description": description,
            "url": url,
            "area": area,
        }
        new_obj = Origin(**{**defaults, **query})
        await cls.do_validation(new_obj)
        obj, created = await Origin.objects.aget_or_create(**query, defaults=defaults)
        return obj


class GathererManager(db_models.Manager):
    def get_by_natural_key(self, name, gather_type):
        return self.get(name=name, gather_type=gather_type)


class Gatherer(
    core_models.ChangedModelBase,
    core_models.NameTitleModelBase,
    core_models.DescriptionUrlModelBase,
    core_models.ModelBase,
):
    """The way the data was obtained."""

    gather_type = db_models.CharField(
        max_length=300,
        help_text="The gather data type name.",
    )

    objects = GathererManager()

    class Meta:
        constraints = [
            db_models.UniqueConstraint(
                fields=["name", "gather_type"],
                name="explore_gatherer_unique_name_gather_type",
            )
        ]

    def natural_key(self):
        return self.name, self.gather_type

    natural_key.dependencies = []

    def __str__(self):
        return f"{self.title} ({self.name})"

    @classmethod
    async def from_obtain_data(
        cls,
        title: str,
        gather_type: str,
        description: str,
        url: str | None = None,
    ) -> "Gatherer":
        query = {"name": slugify(title), "gather_type": gather_type}
        defaults = {"title": title, "description": description, "url": url}

        new_obj = Gatherer(**{**defaults, **query})
        await cls.do_validation(new_obj)

        obj, created = await Gatherer.objects.aget_or_create(**query, defaults=defaults)
        return obj
