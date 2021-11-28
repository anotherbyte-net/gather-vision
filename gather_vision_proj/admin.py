from django.contrib import admin
from django.utils.translation import gettext as _


class GatherVisionAdminSite(admin.AdminSite):
    site_title = _("Vision site admin")
    site_header = _("Vision admin")
    index_title = _("Site admin")


# from django.contrib.auth.models import Group, User
# from django.contrib.auth.admin import GroupAdmin, UserAdmin
