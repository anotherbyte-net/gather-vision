from django.urls import path
from django.views.decorators.cache import cache_page

from gather_vision.views.general import HomeIndexView, AboutIndexView
from gather_vision.views.outages import OutageIndexView
from gather_vision.views.petitions import PetitionIndexView
from gather_vision.views.playlists import PlaylistIndexView
from gather_vision.views.transport import TransportIndexView, TransportDataView

_cache_sec = 60 * 10

app_name = "gather_vision"
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
    path(
        "outages/",
        cache_page(_cache_sec)(OutageIndexView.as_view()),
        name="outages-index",
    ),
    path(
        "petitions/",
        cache_page(_cache_sec)(PetitionIndexView.as_view()),
        name="petitions-index",
    ),
    path(
        "playlists/",
        cache_page(_cache_sec)(PlaylistIndexView.as_view()),
        name="playlists-index",
    ),
    path(
        "transport/<transport_filter>/",
        cache_page(_cache_sec)(TransportIndexView.as_view()),
        name="transport-filter",
    ),
    path(
        "transport/",
        cache_page(_cache_sec)(TransportIndexView.as_view()),
        name="transport-index",
    ),
    path(
        "transport/<transport_filter>/data.<cust_ext>",
        cache_page(_cache_sec)(TransportDataView.as_view()),
        name="transport-data",
    ),
]
