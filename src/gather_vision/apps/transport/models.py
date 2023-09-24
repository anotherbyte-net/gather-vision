import logging
import typing
from datetime import datetime

from django.db import models as db_models
from django.utils.text import slugify

from gather_vision.apps.explore import models as explore_models
from gather_vision.obtain.core import models as core_models, data

logger = logging.getLogger(__name__)


class GroupManager(db_models.Manager):
    def get_by_natural_key(self, name, category):
        return self.get(name=name, category=category)


class Group(
    core_models.ChangedModelBase,
    core_models.NameTitleModelBase,
    core_models.ModelBase,
):
    """
    A transport service.

    For example, for 'train line XZY'.
    The category is 'train', the name is 'XZY'.
    """

    CATEGORY_BUS = "bus"
    CATEGORY_FERRY = "ferry"
    CATEGORY_TRAIN = "train"
    CATEGORY_TRAM = "tram"
    CATEGORY_CHOICES = [
        (CATEGORY_BUS, "Bus"),
        (CATEGORY_FERRY, "Ferry"),
        (CATEGORY_TRAIN, "Train"),
        (CATEGORY_TRAM, "Tram"),
    ]

    category = db_models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="The type of transport.",
    )

    objects = GroupManager()

    class Meta:
        constraints = [
            db_models.UniqueConstraint(
                fields=["name", "category"],
                name="transport_group_unique_name_category",
            )
        ]

    def natural_key(self):
        return self.name, self.category

    def __str__(self):
        return f"transport group {self.title} - {self.category} ({self.name})"

    @classmethod
    async def from_obtain_data(cls, title: str, category: str) -> "Group":
        query = {"name": slugify(title), "category": category}
        defaults = {"title": title}

        new_obj = Group(**{**defaults, **query})
        await cls.do_validation(new_obj)

        obj, created = await Group.objects.aget_or_create(**query, defaults=defaults)
        return obj

    @classmethod
    def guess_categories(
        cls, raw: typing.Iterable[str]
    ) -> typing.Iterable[tuple[str, str]]:
        for item in raw:
            value = slugify(item)
            if all([("ferry" in value or "ferries" in value)]):
                yield item, cls.CATEGORY_FERRY
            if all([("tram" in value)]):
                yield item, cls.CATEGORY_TRAM
            if all([("train" in value)]):
                yield item, cls.CATEGORY_TRAM
            if all([("bus" in value)]):
                yield item, cls.CATEGORY_TRAM


class EventManager(db_models.Manager):
    def get_by_natural_key(self, name, origin):
        return self.get(name=name, origin=origin)


class Event(
    core_models.ChangedModelBase,
    core_models.NameTitleModelBase,
    core_models.RetrievedModelBase,
    core_models.IssuedOccurredModelBase,
    core_models.DescriptionUrlModelBase,
    core_models.ModelBase,
):
    """A transport event."""

    CATEGORY_TRAIN_TRACK = "train_track"
    CATEGORY_TRAIN_STATION = "train_station"
    CATEGORY_TRAIN_CARPARK = "train_carpark"
    CATEGORY_TRAIN_ACCESSIBILITY = "train_accessibility"
    CATEGORY_BUS_STOP = "bus_stop"
    CATEGORY_FERRY_TERMINAL = "ferry_terminal"
    CATEGORY_TRAIN_SERVICE = "train_service"
    CATEGORY_BUS_SERVICE = "bus_service"
    CATEGORY_FERRY_SERVICE = "ferry_service"
    CATEGORY_CHOICES = [
        (CATEGORY_TRAIN_TRACK, "Train track"),
        (CATEGORY_TRAIN_STATION, "Train station"),
        (CATEGORY_TRAIN_CARPARK, "Train carpark"),
        (CATEGORY_TRAIN_ACCESSIBILITY, "Train accessibility"),
        (CATEGORY_BUS_STOP, "Bus stop"),
        (CATEGORY_FERRY_TERMINAL, "Ferry terminal"),
        (CATEGORY_TRAIN_SERVICE, "Train service"),
        (CATEGORY_BUS_SERVICE, "Bus service"),
        (CATEGORY_FERRY_SERVICE, "Ferry service"),
    ]

    SEVERITY_INFO = "info"
    SEVERITY_MINOR = "minor"
    SEVERITY_MAJOR = "major"
    SEVERITY_CHOICES = [
        (SEVERITY_INFO, "Info"),
        (SEVERITY_MINOR, "Minor"),
        (SEVERITY_MAJOR, "Major"),
    ]

    origin = db_models.ForeignKey(
        explore_models.Origin,
        related_name="transport_events",
        on_delete=db_models.CASCADE,
    )
    area = db_models.ForeignKey(
        explore_models.Area,
        blank=True,
        null=True,
        related_name="transport_events",
        on_delete=db_models.PROTECT,
    )
    gatherer = db_models.ForeignKey(
        explore_models.Gatherer,
        related_name="transport_events",
        on_delete=db_models.CASCADE,
        null=True,
    )
    groups = db_models.ManyToManyField(
        Group,
        related_name="events",
        help_text="The groups involved in this event.",
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
    category = db_models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="The infrastructure affected by the event.",
    )
    severity = db_models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        help_text="The severity of the event.",
    )
    # 'locations' is a text description of the more precise Area instances.
    locations = db_models.CharField(
        blank=True,
        max_length=500,
        help_text="The locations covered by the event.",
    )

    objects = EventManager()

    class Meta:
        constraints = [
            db_models.UniqueConstraint(
                fields=["origin", "name"],
                name="transport_event_unique_origin_name",
            )
        ]

    def natural_key(self):
        return (self.name,) + self.origin.natural_key()

    natural_key.dependencies = ["explore.origin"]

    def __str__(self):
        return f"transport event {self.title} ({self.name})"

    @classmethod
    async def from_obtain_data(
        cls,
        title: str,
        retrieved_date: datetime,
        issued_date: datetime,
        occurred_date: datetime,
        description: str,
        url: str,
        origin: explore_models.Origin,
        area: explore_models.Area,
        gatherer: explore_models.Gatherer,
        groups: list[Group],
        start_date: datetime,
        stop_date: datetime,
        category: str,
        severity: str,
        locations: list[str],
    ):
        query = {"name": slugify(title), "origin": origin}
        defaults = {
            "title": title,
            "retrieved_date": retrieved_date,
            "issued_date": issued_date,
            "occurred_date": occurred_date,
            "description": description,
            "url": url,
            "area": area,
            "gatherer": gatherer,
            "start_date": start_date,
            "stop_date": stop_date,
            "category": category,
            "severity": severity,
            "locations": "; ".join(locations),
        }
        new_obj = Event(**{**defaults, **query})
        await cls.do_validation(new_obj)

        obj, created = await Event.objects.aget_or_create(**query, defaults=defaults)

        await obj.groups.aset(groups)

        return obj

    _store_category_raw = set()

    @classmethod
    def guess_category(cls, raw: str) -> str | None:
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("%s category: %s", cls.__name__, raw)

        entries: list[str] = slugify(raw or "").split("-")
        if not entries or not [i for i in entries if i]:
            return None

        if logger.isEnabledFor(logging.DEBUG):
            for i in entries:
                if i:
                    cls._store_category_raw.add(i)
            logger.debug(
                "%s category: %s", cls.__name__, sorted(cls._store_category_raw)
            )

        for event_cat_option in event_cat_options:
            if event_cat_option.check(entries):
                return event_cat_option.label

        return None

        # is_park_n_ride_only = {"park", "n", "ride"}
        # is_station = {"station", "stations", "platform", "platforms", "entrance"}
        # is_access = {"lift", "escalator"}
        # is_train_only = {"track", "tracks", "train" "trains"}
        # is_service = {"route", "service", "timetable", "line"}
        # is_bus_only = {"bus", "buses"}
        # is_ferry_only = {"ferry", "ferries"}
        # is_ferry_stop_only = {"terminal", "terminals"}
        # is_bus_stop_only = {"stop", "stops"}

    @classmethod
    def _category_is_bus_service(cls, entries: list[str]) -> bool:
        for entry in entries:
            if not entry:
                continue
            if entry == "stop":
                continue
            if entry == "ELLIPSIS":
                continue
            # first char can be n, p, digit
            first_char = entry[0].lower()
            if not first_char.isdigit() or first_char not in ["n", "p"]:
                return False
            # rest chars must be digits
            if len(entry) > 1:
                rest_chars = entry[1:]
                if not all(c.isdigit() for c in rest_chars):
                    return False
            return True
        raise NotImplementedError()

    @classmethod
    def _category_is_train_track(cls, entries: list[str]) -> bool:
        for entry in entries:
            if not entry:
                continue
            if entry == "ELLIPSIS" or entry.lower() in ["line", "lines"]:
                return True

        return False

    @classmethod
    def guess_severity(cls, value: str) -> str | None:
        if "Informative" in value:
            return cls.SEVERITY_INFO
        if "Minor" in value:
            return cls.SEVERITY_MINOR
        if "Major" in value:
            return cls.SEVERITY_MAJOR
        return None


event_cat_options = [
    data.GatherDataContainerCheck(
        label=Event.CATEGORY_TRAIN_TRACK,
        required_one=["track"],
        forbidden=["entrance", "station", "bus"],
        allowed=["line", "lines"],
        allow_unmatched=True,
    ),
    data.GatherDataContainerCheck(
        label=Event.CATEGORY_TRAIN_STATION,
        required_one=["entrance", "station"],
        forbidden=["stop", "timetables", "park", "ride", "bus"],
        allowed=lambda x: all(c.isdigit() for c in x),
        allow_unmatched=True,
    ),
    data.GatherDataContainerCheck(
        label=Event.CATEGORY_TRAIN_SERVICE,
        required_one=["line", "lines"],
        forbidden=["bus", "park", "ride", "bus"],
        allow_unmatched=True,
    ),
    data.GatherDataContainerCheck(
        label=Event.CATEGORY_TRAIN_CARPARK,
        required_all=["park", "ride"],
        allow_unmatched=True,
    ),
    data.GatherDataContainerCheck(
        label=Event.CATEGORY_BUS_STOP,
        required_one=["stop", "stops", "bus"],
        forbidden=["park", "ride", "routes", "services"],
        allowed=lambda x: all(c.isdigit() for c in x) or x[0] in ["n"],
        allow_unmatched=True,
    ),
    data.GatherDataContainerCheck(
        label=Event.CATEGORY_BUS_SERVICE,
        required_one=lambda x: x in ["route", "service"]
        or all(c.isdigit() for c in x)
        or x[0] in ["p"],
        forbidden=["park", "ride"],
        allow_unmatched=True,
    ),
    data.GatherDataContainerCheck(
        label=Event.CATEGORY_FERRY_SERVICE,
        required_one=["ferry"],
        allow_unmatched=True,
    ),
]
