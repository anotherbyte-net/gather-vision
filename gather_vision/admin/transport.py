from django.contrib import admin

import gather_vision.models as app_models


@admin.register(app_models.TransportItem)
class TransportItemAdmin(admin.ModelAdmin):
    pass


@admin.register(app_models.TransportLine)
class TransportLineAdmin(admin.ModelAdmin):
    pass
