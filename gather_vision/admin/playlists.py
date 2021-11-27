from django.contrib import admin

import gather_vision.models as app_models
from gather_vision.admin.custom_site import admin_site


@admin_site.register(app_models.PlaylistItem)
class PlaylistItemAdmin(admin.ModelAdmin):
    pass


@admin_site.register(app_models.PlaylistEntry)
class PlaylistEntryAdmin(admin.ModelAdmin):
    pass


@admin_site.register(app_models.PlaylistSource)
class PlaylistSourceAdmin(admin.ModelAdmin):
    pass


@admin_site.register(app_models.PlaylistTrack)
class PlaylistTrackAdmin(admin.ModelAdmin):
    list_filter = ("source",)


@admin_site.register(app_models.PlaylistTrackSource)
class PlaylistTrackSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "title", "info_url")
