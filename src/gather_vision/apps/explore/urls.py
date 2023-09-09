from django.urls import path
from django.views.decorators.cache import cache_page

from gather_vision.apps.explore.views.general import HomeIndexView, AboutIndexView

_cache_sec = 60 * 10

app_name = "explore"

urlpatterns = [
    path(
        "",
        cache_page(_cache_sec)(HomeIndexView.as_view()),
        name="home-index",
    ),
    path(
        "about/",
        cache_page(_cache_sec)(AboutIndexView.as_view()),
        name="about-index",
    ),
]
