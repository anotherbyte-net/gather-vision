from datetime import tzinfo
from typing import Optional, Iterable

from requests import codes

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.component.spotify_client import SpotifyClient
from gather_vision.process.item.track import Track


class Spotify:
    service_name = "spotify"

    key_refresh_token = "SPOTIFY_AUTH_REFRESH_TOKEN"
    key_client_id = "SPOTIFY_AUTH_CLIENT_ID"
    key_client_secret = "SPOTIFY_AUTH_CLIENT_SECRET"
    key_redirect_uri = "SPOTIFY_AUTH_REDIRECT_URI"

    def __init__(
        self,
        logger: Logger,
        http_client: HttpClient,
        normalise: Normalise,
        tz: tzinfo,
        market: str = "AU",
    ):
        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._tz = tz
        self._market = market

        self._client = SpotifyClient(logger, http_client, tz)
        self._access_token: str = ""
        self._refresh_token: str = ""

    def playlist_tracks_get(
        self,
        collection_name: str,
        playlist_id: str,
        limit: Optional[int] = None,
    ) -> Iterable[Track]:
        """Get the tracks in the playlist."""
        self._logger.info("Retrieving tracks for Spotify playlist.")
        status, content = self._client.playlist_tracks_get(
            access_token=self._access_token,
            playlist_id=playlist_id,
            limit=limit,
            offset=0,
            market=self._market,
        )

        tracks = []
        for index, track in enumerate(content.get("items", [])):
            track_number = index + 1
            item = track.get("track", {})
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
        self._logger.info(
            f"Setting new tracks for Spotify playlist '{collection_name}'."
        )
        song_ids = [t.track_id for t in new_tracks]
        status, content = self._client.playlist_tracks_set(
            access_token=self._access_token,
            playlist_id=playlist_id,
            song_ids=song_ids,
        )
        return status == codes.created

    def playlist_details_set(
        self,
        collection_name: str,
        playlist_id: str,
        title: str = None,
        description: str = None,
        is_public: bool = None,
    ):
        """Set playlist details."""
        self._logger.info(f"Setting details for Spotify playlist '{collection_name}'.")
        status, content = self._client.playlist_details_set(
            access_token=self._access_token,
            playlist_id=playlist_id,
            title=title,
            description=description,
            is_public=is_public,
        )
        return status == codes.ok

    def track_query_get(
        self,
        collection_name: str,
        query: str,
        limit: int = 5,
    ) -> Iterable[Track]:
        """Find matching tracks."""
        self._logger.info(f"Looking for Spotify track matching '{query}'")
        tracks = []
        query_status, query_result = self._client.track_query_get(
            access_token=self._access_token,
            query=query,
            limit=limit,
        )

        # stop if there are results
        track_hits = query_result.get("tracks", {}).get("items", [])
        if not query_result or not track_hits:
            return []

        for index, item in enumerate(track_hits):
            track_number = index + 1
            track = self._build_track(collection_name, track_number, item)
            tracks.append(track)
        return tracks

    def login_init(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Run the initial authorisation flow to get an access token and refresh token.
        """
        self._access_token, self._refresh_token, expires_in = self._client.login_init(
            client_id, client_secret, redirect_uri
        )

    def login_next(self, client_id: str, client_secret: str, refresh_token: str):
        """Get the next login token."""
        self._access_token = self._client.login_token_next(
            client_id, client_secret, refresh_token
        )

    def _build_track(
        self,
        collection_name: str,
        track_number: int,
        item: dict,
    ) -> Track:
        track_id = item.get("id")
        track_name = item.get("name")
        track_artists = [a.get("name") for a in item.get("artists")]

        (
            title_norm,
            primary_artists_norm,
            featured_artists_norm,
            queries,
        ) = self._normalise.track(track_name, track_artists, [])

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
