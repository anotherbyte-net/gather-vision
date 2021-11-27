from datetime import tzinfo
from typing import Optional, Iterable

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.component.youtube_music_client import (
    YoutubeMusicClient,
)
from gather_vision.process.item.track import Track


class YoutubeMusic:
    service_name = "ytmusic"

    key_config = "YOUTUBE_MUSIC_AUTH_CONFIG"

    def __init__(
        self, logger: Logger, http_client: HttpClient, normalise: Normalise, tz: tzinfo
    ):
        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._tz = tz

        self._client = YoutubeMusicClient(logger, http_client, tz)
        self._credentials: str = ""

    def playlist_tracks_get(
        self,
        collection_name: str,
        playlist_id: str,
        limit: Optional[int] = None,
    ) -> Iterable[Track]:
        """Get the tracks in the playlist."""
        self._logger.info(f"Retrieving tracks for YouTube Music playlist.")
        items = self._client.playlist_tracks_get(playlist_id, limit)
        tracks = []
        for index, item in enumerate(items):
            track_number = index + 1
            track = self._build_track(collection_name, track_number, item)
            tracks.append(track)
        return tracks

    def playlist_tracks_set(
        self,
        collection_name: str,
        playlist_id: str,
        new_tracks: Iterable[Track],
        old_tracks: Iterable[Track],
    ) -> bool:
        """Replace songs in a playlist."""
        msg = f"Setting new tracks for YouTube Music playlist '{collection_name}'."
        self._logger.info(msg)
        return self._client.playlist_tracks_set(playlist_id, new_tracks, old_tracks)

    def playlist_details_set(
        self,
        collection_name: str,
        playlist_id: str,
        title: str = None,
        description: str = None,
        is_public: bool = None,
    ):
        """Set playlist details."""
        self._logger.info(
            f"Setting details for YouTube Music playlist '{collection_name}'."
        )
        result = self._client.playlist_details_set(
            playlist_id=playlist_id,
            title=title,
            description=description,
            is_public=is_public,
        )
        return result == "STATUS_SUCCEEDED"

    def track_query_get(
        self,
        collection_name: str,
        query: str,
        limit: int = 5,
    ) -> Iterable[Track]:
        """Find matching tracks."""
        self._logger.debug(f"Looking for YouTube Music track matching '{query}'.")
        query_result = self._client.track_query_get(query=query, limit=limit)

        tracks = []
        for index, item in enumerate(query_result):
            track_number = index + 1
            track = self._build_track(collection_name, track_number, item)
            tracks.append(track)
        return tracks

    def login_init(self):
        """Run the initial authorisation flow to get the credentials."""
        self._credentials = self._client.login_init()

    def login_next(self, credentials: str):
        """Get the next login token."""
        self._credentials = credentials
        self._client.login_token_next(credentials)

    def _build_track(
        self,
        collection_name: str,
        track_number: int,
        item: dict,
    ) -> Track:
        track_id = item.get("videoId")
        track_title = item.get("title")
        track_artists = [a.get("name") for a in item.get("artists")]

        (
            title_norm,
            primary_artists_norm,
            featured_artists_norm,
            queries,
        ) = self._normalise.track(track_title, track_artists, [])

        track = Track(
            service_name=self.service_name,
            collection_name=collection_name,
            track_number=track_number,
            track_id=track_id,
            title=title_norm,
            primary_artists=primary_artists_norm,
            featured_artists=featured_artists_norm,
            queries=queries,
            raw=item,
        )
        return track
