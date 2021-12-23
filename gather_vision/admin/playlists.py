from django.contrib import admin

import gather_vision.models as app_models


@admin.register(app_models.PlaylistItem)
class PlaylistItemAdmin(admin.ModelAdmin):
    list_display = ("source", "retrieved_date")
    date_hierarchy = "retrieved_date"
    list_filter = ("source__title",)
    search_fields = ("entries__position", "entries__position_change")


@admin.register(app_models.PlaylistEntry)
class PlaylistEntryAdmin(admin.ModelAdmin):
    list_display = ("playlist", "position", "position_change")
    date_hierarchy = "modified_date"
    list_filter = ("playlist__source__title",)
    search_fields = (
        "position",
        "position_change",
        "tracks__title",
        "tracks__artists",
        "tracks__code",
    )
    ordering = ("playlist", "position")
    filter_horizontal = ("tracks",)


@admin.register(app_models.PlaylistTrack)
class PlaylistTrackAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "artists",
        "source",
        "code",
        "musicbrainz_code",
    )
    date_hierarchy = "modified_date"
    list_filter = ("source__title",)
    search_fields = ("code", "title", "artists")
