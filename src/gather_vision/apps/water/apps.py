from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WaterAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gather_vision.apps.water"
    verbose_name = _("Water")
