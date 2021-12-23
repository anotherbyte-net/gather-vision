from django.views.generic import TemplateView
from django.utils.translation import gettext as _


class ContactTracingIndexView(TemplateView):
    template_name = "gather_vision/contact_tracing/index.html"
    page_title = _("Contact Tracing")
