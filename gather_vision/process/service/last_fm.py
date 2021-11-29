from datetime import datetime, tzinfo
from typing import Optional

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.item.playlist import Playlist


class LastFm:
    """Get playlists from Last.fm."""

    service_name = "lastfm"
    service_title = "Last.fm"
    collection_names = ["most_popular"]
    collection_titles = ["Most Popular"]

    key_api_key = "LASTFM_AUTH_API_KEY"

    def __init__(
        self, logger: Logger, http_client: HttpClient, normalise: Normalise, tz: tzinfo
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

    def get_playlist(
        self,
        name: str,
        title: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Playlist:
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
            f"from '{self.service_name}' collection '{name}'."
        )

        config = self._collection_config[name]
        params = self.build_qs(**config, limit=limit)

        data = self._http_client.get(self._url, params=params)
        if data:
            data = data.json().get("tracks", {}).get("track", {})
        else:
            data = []

        # build the playlist
        playlist = Playlist(
            name=f"{self.service_name}_{name}",
            title=f"{self.service_title} {title}",
        )
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
                service_name=self.service_name,
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
            f"from '{self.service_name}' collection '{name}'."
        )
        return playlist

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

    def login_next(self, api_key: str):
        """Get the next login token."""
        self._api_key = api_key
