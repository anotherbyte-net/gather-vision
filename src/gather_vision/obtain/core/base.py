from django.db import models


class ModelBase(models.Model):
    class Meta:
        abstract = True


class ModelChangedMixin:
    """A mixin to provide created and modified date for a model."""

    created_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        help_text="The date this record was created.",
    )
    modified_date = models.DateTimeField(
        auto_now=True,
        editable=False,
        help_text="The date this record was most recently changed.",
    )


class ModelRetrievedMixin:
    """A mixin to provide retrieved date for a model."""

    retrieved_date = models.DateTimeField(
        editable=False,
        help_text="The date this record was retrieved.",
    )


class ModelIssuedOccurredMixin:
    """A mixin to provide issued and occurred date for a model."""

    issued_date = models.DateTimeField(
        editable=False,
        help_text="The date this record was issued.",
    )
    occurred_date = models.DateTimeField(
        editable=False,
        help_text="The date this record occurred.",
    )


class ModelDescriptionUrlMixin:
    """A mixin to provide description and url for a model."""

    description = models.TextField(
        help_text="The description of the record.",
    )
    url = models.URLField(
        blank=True,
        help_text="A link to the record details.",
    )


class ModelNameTitleMixin:
    """A mixin to provide name and title for a model."""

    name = models.SlugField(
        help_text="The internal name of the record.",
    )
    title = models.CharField(
        max_length=200,
        help_text="The displayed title.",
    )
