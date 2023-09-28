from django.urls import path
from django_distill import distill_path
from django.views.decorators.cache import cache_page

from gather_vision.apps.explore.views.general import HomeIndexView, AboutIndexView

_cache_sec = 60 * 10

app_name = "explore"

urlpatterns = [
    distill_path(
        "",
        cache_page(_cache_sec)(HomeIndexView.as_view()),
        name="home-index",
        distill_file=f"{app_name}/index.html",
    ),
    distill_path(
        "about/",
        cache_page(_cache_sec)(AboutIndexView.as_view()),
        name="about-index",
        distill_file=f"{app_name}/about/index.html",
    ),
]
