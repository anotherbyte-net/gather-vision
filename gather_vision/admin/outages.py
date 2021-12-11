from django.contrib import admin

import gather_vision.models as app_models


@admin.register(app_models.OutageItem)
class OutageItemAdmin(admin.ModelAdmin):
    list_display = (
        "group",
        "customers",
        "council",
        "suburb",
        "post_code",
        "cause",
        "restored_date",
        "source",
    )
    date_hierarchy = "restored_date"
    list_filter = ("source__title", "council", "cause")
    search_fields = (
        "event_name",
        "council",
        "suburb",
        "post_code",
        "cause",
        "streets",
    )
    ordering = ("-modified_date",)


class OutageItemInlineAdmin(admin.TabularInline):
    model = app_models.OutageItem
    can_delete = False
    show_change_link = True
    extra = 0
    fields = (
        "customers",
        "council",
        "suburb",
        "post_code",
        "cause",
        "restored_date",
    )
    readonly_fields = (
        "customers",
        "council",
        "suburb",
        "post_code",
        "cause",
        "restored_date",
    )


@admin.register(app_models.OutageGroup)
class OutageGroupAdmin(admin.ModelAdmin):
    list_display = (
        "total_customers",
        "demand",
        "rating",
        "source_updated_date",
        "retrieved_date",
    )
    date_hierarchy = "source_updated_date"
    list_filter = ("rating",)
    search_fields = ("demand", "total_customers")
    inlines = [OutageItemInlineAdmin]
    ordering = ("-retrieved_date",)
