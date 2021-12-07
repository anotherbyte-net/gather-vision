from django.contrib import admin

import gather_vision.models as app_models


@admin.register(app_models.PetitionChange)
class PetitionChangeAdmin(admin.ModelAdmin):
    list_display = ("retrieved_date", "signatures", "petition")
    date_hierarchy = "retrieved_date"
    list_filter = ("petition__source__title",)
    search_fields = ("signatures", "petition__title", "petition__code")
    ordering = ("-retrieved_date",)


class PetitionChangeInlineAdmin(admin.TabularInline):
    model = app_models.PetitionChange
    can_delete = False
    show_change_link = True
    extra = 0
    readonly_fields = ("retrieved_date", "signatures")


@admin.register(app_models.PetitionItem)
class PetitionItemAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "opened_date", "closed_date")
    date_hierarchy = "closed_date"
    list_filter = ("source__title", "eligibility")
    search_fields = ("title", "code", "principal", "sponsor", "body")
    inlines = [
        PetitionChangeInlineAdmin,
    ]
    ordering = ("-closed_date",)
