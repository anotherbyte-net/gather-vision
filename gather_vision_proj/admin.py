from django.contrib import admin
from django.utils.translation import gettext as _


class GatherVisionAdminSite(admin.AdminSite):
    site_title = _("Vision site admin")
    site_header = _("Vision admin")
    index_title = _("Site admin")
