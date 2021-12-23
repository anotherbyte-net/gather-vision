from django.db import models
from django.utils.translation import gettext as _
from gather_vision.models import InformationSource
from gather_vision.models.abstract_base import AbstractBase
from gather_vision.process.service.transport.qld_rail_events import QldRailEvents
from gather_vision.process.service.transport.translink_notices import TranslinkNotices


class TransportItem(AbstractBase):
    """A transport notice item."""

    source = models.ForeignKey(
        InformationSource,
        related_name="transport_items",
        on_delete=models.CASCADE,
    )
    source_identifier = models.CharField(
        max_length=200,
        help_text="The identifier for this transport notice from the source.",
    )
    lines = models.ManyToManyField(
        "TransportLine",
        related_name="notices",
        help_text="The lines involved in this transport notice.",
    )
    title = models.CharField(
        max_length=200,
        help_text="The title of the transport notice.",
    )
    body = models.TextField(
        blank=True,
        help_text="The text of the transport notice.",
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text="The start date of this transport notice.",
    )
    stop_date = models.DateField(
        blank=True,
        null=True,
        help_text="The finish date this transport notice.",
    )
    is_train = models.BooleanField(
        # IsTrain
        help_text="Whether the transport notice includes train services.",
    )
    view_url = models.URLField(
        # Link
        blank=True,
        help_text="The url to view the transport notice.",
    )
    notice_type = models.CharField(
        # EventType
        blank=True,
        max_length=200,
        help_text="The type of the transport notice.",
    )
    category = models.CharField(
        # Category
        blank=True,
        max_length=200,
        help_text="The category of the transport notice.",
    )
    severity = models.CharField(
        # Severity
        blank=True,
        max_length=200,
        help_text="The severity of the transport notice.",
    )
    timing = models.CharField(
        # When
        blank=True,
        max_length=200,
        help_text="The timing of the transport notice.",
    )
    location = models.CharField(
        # Locations
        blank=True,
        max_length=500,
        help_text="The location covered by the transport notice.",
    )

    def __str__(self):
        txt = f'{self.source}: "{self.title}"'
        if self.start_date:
            txt += f" starting {self.start_date.isoformat()}"
        if self.stop_date:
            txt += f" ending {self.stop_date.isoformat()}"
        return txt

    def long_str(self):
        text = ""
        sep = "; "

        if self.source.name:
            text += {
                QldRailEvents.code: QldRailEvents.short_title,
                TranslinkNotices.code: TranslinkNotices.short_title,
            }[self.source.name] + ":"

        if self.start_date:
            text += f" starting {self.start_date.isoformat()}"
        if self.stop_date:
            text += f" ending {self.stop_date.isoformat()}"

        if self.title and self.body:
            text += " " + self.title + " - " + self.body
        elif self.title and not self.body:
            text += " " + self.title
        elif not self.title and self.body:
            text += " " + self.body

        if self.is_train:
            text += sep + "Train"

        if self.lines:
            text += sep + "Lines : " + ", ".join([str(i) for i in self.get_lines()])

        if self.notice_type:
            text += sep + self.prop_notice_type

        if self.category:
            text += sep + self.prop_category

        if self.severity:
            text += sep + self.prop_severity

        if self.timing:
            text += sep + self.prop_timing

        if self.location:
            text += sep + self.prop_location

        if self.view_url:
            text += sep + "Url: " + self.view_url

        return text

    def long_dict(self):
        return {
            "source": self.source.long_dict(),
            "source_identifier": self.source_identifier,
            "lines": [str(i) for i in self.get_lines()],
            "title": self.title,
            "body": self.body,
            "start_date": self.start_date,
            "stop_date": self.stop_date,
            "is_train": self.is_train,
            "view_url": self.view_url,
            "notice_type": self.prop_notice_type,
            "category": self.prop_category,
            "severity": self.prop_severity,
            "timing": self.prop_timing,
            "location": self.prop_location,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
        }

    @classmethod
    def long_csv_headers(cls):
        return [
            "source_name",
            "source_title",
            "source_identifier",
            "lines",
            "title",
            "body",
            "start_date",
            "stop_date",
            "is_train",
            "view_url",
            "notice_type",
            "category",
            "severity",
            "timing",
            "location",
            "created_date",
            "modified_date",
            "source_created_date",
            "source_modified_date",
            "source_info_url",
        ]

    def long_csv(self):
        source = self.source.long_csv()
        source_name = source["name"]
        source_title = source["title"]
        source_info_url = source["info_url"]
        source_created_date = source["created_date"]
        source_modified_date = source["modified_date"]
        return {
            "source_name": source_name,
            "source_title": source_title,
            "source_info_url": source_info_url,
            "source_created_date": source_created_date,
            "source_modified_date": source_modified_date,
            "source_identifier": self.source_identifier,
            "lines": ";".join([str(i) for i in self.get_lines()]),
            "title": self.title,
            "body": self.body,
            "start_date": self.start_date,
            "stop_date": self.stop_date,
            "is_train": self.is_train,
            "view_url": self.view_url,
            "notice_type": self.prop_notice_type,
            "category": self.prop_category,
            "severity": self.prop_severity,
            "timing": self.prop_timing,
            "location": self.prop_location,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
        }

    @property
    def prop_notice_type(self):
        return self.notice_type.title() if self.notice_type else ""

    @property
    def prop_category(self):
        return self.category.title() if self.category else ""

    @property
    def prop_severity(self):
        return self.severity.title() if self.severity else ""

    @property
    def prop_timing(self):
        return self.timing.title() if self.timing else ""

    @property
    def prop_location(self):
        return self.location.title() if self.location else ""

    @property
    def date_range(self):
        same_day = (
            self.start_date.isoformat()
            if self.start_date
            else "" == self.stop_date.isoformat()
            if self.stop_date
            else ""
        )
        f = "%a, %d %b %Y"
        if self.start_date and self.stop_date and not same_day:
            return _(
                f"From {self.start_date.strftime(f)} "
                f"to {self.stop_date.strftime(f)}"
            )
        if self.start_date and self.stop_date and same_day:
            return _(f"On {self.start_date.strftime(f)}")
        elif self.start_date and not self.stop_date:
            return _(f"From {self.start_date.strftime(f)}")
        elif not self.start_date and self.stop_date:
            return _(f"To {self.stop_date.strftime(f)}")
        else:
            raise ValueError()

    @classmethod
    def get_items(cls, **kwargs):
        query = cls.objects.order_by("start_date", "stop_date")
        if kwargs:
            query = query.filter(**kwargs)
        query = query.prefetch_related("source", "lines")
        return query

    @classmethod
    def get_items_track_closures(cls):
        return cls.get_items(is_train=True, category__in=["station", "track"])

    @classmethod
    def get_items_track_access(cls):
        return cls.get_items(
            is_train=True, category__in=["station", "track", "accessibility", "carpark"]
        )

    @classmethod
    def get_items_available(cls):
        return {
            "all": cls.get_items,
            "track-closures": cls.get_items_track_closures,
            "track-access": cls.get_items_track_access,
        }

    def get_lines(self):
        return sorted((i for i in self.lines.all()), key=lambda x: str(x.title))

    @property
    def tags(self):
        if self.is_train:
            yield {"title": "Train", "classes": "bg-dark"}
        if self.notice_type:
            yield {"title": f"Type: {self.prop_notice_type}", "classes": "bg-secondary"}
        if self.category:
            yield {
                "title": f"Category: {self.prop_category}",
                "classes": "bg-info text-dark",
            }
        if self.severity:
            s = self.prop_severity
            yield {
                "title": f"Severity: {s}",
                "classes": "bg-warning text-dark" if s != "Major" else "bg-danger",
            }
        if self.timing:
            yield {"title": f"Timing: {self.prop_timing}", "classes": "bg-secondary"}
        if self.location:
            yield {"title": f"Where: {self.prop_location}", "classes": "bg-secondary"}
        if self.lines:
            for line in self.get_lines():
                yield {"title": f"Line: {str(line)}", "classes": "bg-secondary"}
