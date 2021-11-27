from django.views.generic import TemplateView
from django.utils.translation import gettext as _


class TransportIndexView(TemplateView):
    template_name = "gather_vision/transport/index.html"
    page_title = _("Transport")
