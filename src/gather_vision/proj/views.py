from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = "gather_vision/home.html"
