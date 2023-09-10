"""Base model and mixins."""
from django.db import models as db_models


class ModelBase(db_models.Model):
    """A base class for all gather vision Django models."""

    class Meta:
        abstract = True


class ChangedModelBase(db_models.Model):
    """A mixin to provide created and modified date for a model."""

    created_date = db_models.DateTimeField(
        auto_now_add=True,
        editable=False,
        help_text="The date this record was created.",
    )
    modified_date = db_models.DateTimeField(
        auto_now=True,
        editable=False,
        help_text="The date this record was most recently changed.",
    )

    class Meta:
        abstract = True


class RetrievedModelBase(db_models.Model):
    """A mixin to provide retrieved date for a model."""

    retrieved_date = db_models.DateTimeField(
        help_text="The date this record was retrieved.",
    )

    class Meta:
        abstract = True


class IssuedOccurredModelBase(db_models.Model):
    """A mixin to provide issued and occurred date for a model."""

    issued_date = db_models.DateTimeField(
        null=True,
        help_text="The date this record was issued.",
    )
    occurred_date = db_models.DateTimeField(
        null=True,
        help_text="The date this record occurred.",
    )

    class Meta:
        abstract = True


class DescriptionUrlModelBase(db_models.Model):
    """A mixin to provide description and url for a model."""

    description = db_models.TextField(
        blank=True,
        help_text="The description of the record.",
    )
    url = db_models.URLField(
        blank=True,
        help_text="A link to the record details.",
    )

    class Meta:
        abstract = True


class NameTitleModelBase(db_models.Model):
    """A mixin to provide name and title for a model."""

    name = db_models.SlugField(
        help_text="The internal name of the record.",
    )
    title = db_models.CharField(
        max_length=200,
        help_text="The displayed title.",
    )

    class Meta:
        abstract = True
