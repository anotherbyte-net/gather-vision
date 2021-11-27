from django.contrib.admin import AdminSite
from django.utils.translation import gettext as _


class GatherVisionAdminSite(AdminSite):
    site_title = _("Vision site admin")
    site_header = _("Vision administration")
    index_title = _("Site administration")


admin_site = GatherVisionAdminSite(name="vision_admin")
