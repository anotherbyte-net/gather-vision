from django.contrib import admin

import gather_vision.models as app_models


@admin.register(app_models.TransportItem)
class TransportItemAdmin(admin.ModelAdmin):
    list_display = (
        "source_identifier",
        "title",
        "start_date",
        "stop_date",
        "notice_type",
        "category",
        "severity",
        "timing",
        "is_train",
    )

    list_filter = (
        "notice_type",
        "category",
        "severity",
        "timing",
        "is_train",
        "source__title",
        "lines__title",
    )
    search_fields = (
        "title",
        "body",
    )


@admin.register(app_models.TransportLine)
class TransportLineAdmin(admin.ModelAdmin):
    list_display = ("title",)
    date_hierarchy = "modified_date"
    list_filter = ("notices__source__title",)
