from django.views.generic import TemplateView
from django.utils.translation import gettext as _


class PetitionIndexView(TemplateView):
    template_name = "gather_vision/petitions/index.html"
    page_title = _("Petitions")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["graph_data"] = [{"testing": True}]
        return context
