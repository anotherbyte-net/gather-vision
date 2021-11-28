from django.contrib import admin

import gather_vision.models as app_models


@admin.register(app_models.PlaylistItem)
class PlaylistItemAdmin(admin.ModelAdmin):
    pass


@admin.register(app_models.PlaylistEntry)
class PlaylistEntryAdmin(admin.ModelAdmin):
    pass


@admin.register(app_models.PlaylistTrack)
class PlaylistTrackAdmin(admin.ModelAdmin):
    list_filter = ("source",)
