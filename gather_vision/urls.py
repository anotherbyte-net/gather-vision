from django.urls import path

from gather_vision.views.general import HomeIndexView
from gather_vision.views.outages import OutageIndexView
from gather_vision.views.petitions import PetitionIndexView
from gather_vision.views.playlists import PlaylistIndexView
from gather_vision.views.transport import TransportIndexView

app_name = "gather_vision"
urlpatterns = [
    path("", HomeIndexView.as_view(), name="home-index"),
    path("outages/", OutageIndexView.as_view(), name="outages-index"),
    path("petitions/", PetitionIndexView.as_view(), name="petitions-index"),
    path("playlists/", PlaylistIndexView.as_view(), name="playlists-index"),
    path("transport/", TransportIndexView.as_view(), name="transport-index"),
]
