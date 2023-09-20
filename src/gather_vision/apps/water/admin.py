from django.contrib import admin


class StationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "origin",
        "area",
        "coordinate",
    )
    date_hierarchy = "modified_date"
    list_filter = ("origin__title",)
    ordering = ("title",)


class GroupAdmin(admin.ModelAdmin):
    pass


class MeasureAdmin(admin.ModelAdmin):
    list_display = (
        "station",
        "group",
        "level",
        "category",
        "quality",
        "occurred_date",
    )
    list_filter = (
        "category",
        "quality",
        "station__title",
        "group__title",
    )
    search_fields = (
        "level",
        "category",
        "category",
        "quality",
        "station__title",
        "station__name",
        "group__title",
        "group__name",
    )
    date_hierarchy = "occurred_date"
    ordering = ("-occurred_date",)
