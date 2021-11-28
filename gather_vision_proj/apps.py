from django.contrib.admin.apps import AdminConfig


class GatherVisionAdminConfig(AdminConfig):
    default_site = "gather_vision_proj.admin.GatherVisionAdminSite"
