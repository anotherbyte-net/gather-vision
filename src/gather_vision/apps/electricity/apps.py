from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ElectricityAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gather_vision.apps.electricity"
    verbose_name = _("Electricity")
