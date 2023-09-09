from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext as _

import gather_vision.apps.electricity.admin as electricity_admin
import gather_vision.apps.electricity.models as electricity_models
import gather_vision.apps.explore.admin as explore_admin
import gather_vision.apps.explore.models as explore_models
import gather_vision.apps.water.admin as water_admin
import gather_vision.apps.water.models as water_models


class GatherVisionAdminSite(AdminSite):
    site_title = _("Gather Vision Web site admin")
    site_header = _("Gather Vision Web admin")
    index_title = _("Gather Vision Web Site admin")


admin_site = GatherVisionAdminSite()
admin.site = admin_site

admin_site.register(explore_models.CustomUser, UserAdmin)
admin_site.register(Group, GroupAdmin)

admin_site.register(electricity_models.Event, electricity_admin.EventAdmin)
admin_site.register(electricity_models.Progress, electricity_admin.ProgressAdmin)
admin_site.register(electricity_models.Usage, electricity_admin.UsageAdmin)

admin_site.register(explore_models.Origin, explore_admin.OriginAdmin)
admin_site.register(explore_models.Coordinate, explore_admin.CoordinateAdmin)
admin_site.register(explore_models.Area, explore_admin.AreaAdmin)

admin_site.register(water_models.Station, water_admin.StationAdmin)
admin_site.register(water_models.Group, water_admin.GroupAdmin)
admin_site.register(water_models.Measure, water_admin.MeasureAdmin)
#
# admin_site.register(transport_models.Event, transport_admin.EventAdmin)
# admin_site.register(transport_models.Group, transport_admin.GroupAdmin)
#
# admin_site.register(legislatures_models.Entry, legislatures_admin.EntryAdmin)
# admin_site.register(legislatures_models.Progress, legislatures_admin.ProgressAdmin)
