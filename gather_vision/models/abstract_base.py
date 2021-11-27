from django.db import models


class AbstractBase(models.Model):
    """The abstract base model for hill models."""

    created_date = models.DateTimeField(
        auto_now_add=True, help_text="The date this item was created."
    )
    modified_date = models.DateTimeField(
        auto_now=True, help_text="The date this item was last changed."
    )

    class Meta:
        abstract = True
        ordering = ["modified_date"]
