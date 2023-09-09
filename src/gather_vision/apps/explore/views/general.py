from django.views.generic import TemplateView
from django.utils.translation import gettext as _


class HomeIndexView(TemplateView):
    template_name = "explore/home/index.html"
    page_title = _("Home")


class AboutIndexView(TemplateView):
    template_name = "explore/about/index.html"
    page_title = _("About")
