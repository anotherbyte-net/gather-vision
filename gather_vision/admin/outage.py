from django.contrib import admin

import gather_vision.models as app_models
from gather_vision.admin.custom_site import admin_site


@admin_site.register(app_models.OutageItem)
class OutageItemAdmin(admin.ModelAdmin):
    pass


@admin_site.register(app_models.OutageChange)
class OutageChangeAdmin(admin.ModelAdmin):
    pass
