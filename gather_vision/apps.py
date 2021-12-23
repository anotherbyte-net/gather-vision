from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GatherVisionConfig(AppConfig):
    # ref: https://docs.djangoproject.com/en/4.0/ref/contrib/admin/#overriding-the-default-admin-site  # noqa: E501
    default_auto_field = "django.db.models.BigAutoField"
    name = "gather_vision"
    verbose_name = _("Gather Vision")
