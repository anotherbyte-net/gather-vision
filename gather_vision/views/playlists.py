from django.views.generic import TemplateView
from django.utils.translation import gettext as _


class PlaylistIndexView(TemplateView):
    template_name = "gather_vision/playlists/index.html"
    page_title = _("Playlists")
