from django.views.generic import TemplateView
from django.utils.translation import gettext as _


class OutageIndexView(TemplateView):
    template_name = "gather_vision/outages/index.html"
    page_title = _("Outages")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["graph_data"] = [{"testing": True}]
        return context
