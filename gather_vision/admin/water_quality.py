from django.contrib import admin

import gather_vision.models as app_models


@admin.register(app_models.WaterQualitySample)
class WaterQualitySampleAdmin(admin.ModelAdmin):
    list_display = (
        "sample_date",
        "sample_value",
        "sample_status",
    )

    list_filter = (
        "site__title",
        "sample_status",
    )
    search_fields = (
        "sample_value",
        "sample_status",
    )
    date_hierarchy = "sample_date"
    ordering = ("-sample_date",)


@admin.register(app_models.WaterQualitySite)
class WaterQualitySiteAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "latitude", "longitude", "code")
    date_hierarchy = "modified_date"
    list_filter = ("source__title",)
    ordering = ("title",)
