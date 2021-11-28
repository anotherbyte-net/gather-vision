from django.contrib import admin

import gather_vision.models as app_models


@admin.register(app_models.PetitionChange)
class PetitionChangeAdmin(admin.ModelAdmin):
    list_display = ("retrieved_date", "signatures")
    date_hierarchy = "retrieved_date"
    list_filter = ("petition__source__title",)
    search_fields = ("signatures", "petition__title", "petition__code")


@admin.register(app_models.PetitionItem)
class PetitionItemAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "opened_date", "closed_date")
    date_hierarchy = "opened_date"
    list_filter = ("source__title",)
    search_fields = ("title", "code", "principal", "sponor", "body")