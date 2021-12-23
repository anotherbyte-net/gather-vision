from datetime import datetime
from typing import Optional

from zoneinfo import ZoneInfo

from gather_vision.process import item as app_items
from gather_vision import models as app_models
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.service.playlist import abstract as service_mixins


class LastFm(
    service_mixins.PlaylistDetails,
    service_mixins.AuthRequiredService,
    service_mixins.PlaylistSource,
):
    """Get playlists from Last.fm."""

    @property
    def code(self):
        return "lastfm"

    @property
    def title(self):
        return "Last.fm"

    @property
    def collections(self):
        return ["most_popular"]

    def __init__(
        self,
        logger: Logger,
        http_client: HttpClient,
        normalise: Normalise,
        tz: ZoneInfo,
    ):
        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._tz = tz

        self._api_key = None

        self._url = "https://ws.audioscrobbler.com/2.0/"
        self._collection_config = {
            "most_popular": {
                "method": "geo.gettoptracks",
                "country": "australia",
            }
        }

    def get_playlist(self, identifier: str, name: str, title: str):
        playlist = app_items.Playlist(name=name, title=title)
        return playlist

    def get_playlist_tracks(
        self,
        identifier: str,
        name: str,
        title: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ):
        # set the limit
        if not limit:
            limit = 100
        elif limit < 1:
            limit = 1

        # build the url
        if name not in self._collection_config:
            raise ValueError(f"Unrecognised collection name '{name}'.")

        # download the tracks
        self._logger.info(
            f"Downloading up to {limit} tracks "
            f"from '{self.code}' collection '{name}'."
        )

        config = self._collection_config[name]
        params = self.build_qs(**config, limit=limit)

        data = self._http_client.get(self._url, params=params)
        if data:
            data = data.json().get("tracks", {}).get("track", {})
        else:
            data = []

        # build the playlist
        playlist = self.get_playlist(identifier, name, title)
        for index, item in enumerate(data):
            track_number = index + 1
            track_id = item.get("url")
            track_title = item["name"]
            artists = item["artist"]["name"]

            # normalise title and artists
            (
                title_norm,
                primary_artists_norm,
                featured_artists_norm,
                queries,
            ) = self._normalise.track(track_title, artists, "")

            # add track to playlist
            playlist.add_track(
                service_name=self.code,
                collection_name=name,
                track_number=track_number,
                track_id=track_id,
                title=title_norm,
                primary_artists=primary_artists_norm,
                featured_artists=featured_artists_norm,
                queries=queries,
                raw=item,
            )

        self._logger.info(
            f"Retrieved {len(playlist.tracks)} tracks "
            f"from '{self.code}' collection '{name}'."
        )
        return playlist

    def get_model_track(
        self,
        info: app_models.InformationSource,
        track: app_items.Track,
    ):
        code = None
        title = None
        artists = None
        info_url = None
        image_url = None
        musicbrainz_code = None
        obj, created = app_models.PlaylistTrack.objects.update_or_create(
            source=info,
            code=code,
            defaults={
                "title": title,
                "artists": artists,
                "info_url": info_url,
                "image_url": image_url,
                "musicbrainz_code": musicbrainz_code,
            },
        )
        return obj

    def login_init(self, *args, **kwargs):
        pass

    def login_next(self, api_key: str):
        """Get the next login token."""
        self._api_key = api_key

    def build_qs(
        self,
        method: str,
        country: str,
        output_format: str = "json",
        limit: int = 50,
        page: int = 1,
    ):
        if not method:
            raise ValueError("Must provide method.")
        if not country:
            raise ValueError("Must provide country.")
        if not output_format or output_format not in ["json"]:
            raise ValueError("Must provide output format, one of 'json'.")
        if not limit or limit < 1:
            raise ValueError("Must provide limit greater than 0.")
        if not page or page < 1:
            raise ValueError("Must provide page greater than 0.")

        qs = {
            "api_key": self._api_key,
            "method": method,
            "country": country,
            "format": output_format,
            "limit": limit,
            "page": page,
        }
        return qs
