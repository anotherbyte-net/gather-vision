from django.contrib import admin

import gather_vision.models as app_models


@admin.register(app_models.OutageItem)
class OutageItemAdmin(admin.ModelAdmin):
    pass


@admin.register(app_models.OutageChange)
class OutageChangeAdmin(admin.ModelAdmin):
    pass
