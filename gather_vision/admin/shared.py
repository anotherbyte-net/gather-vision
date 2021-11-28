from django.contrib import admin

import gather_vision.models as app_models


@admin.register(app_models.InformationSource)
class InformationSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "info_url")
