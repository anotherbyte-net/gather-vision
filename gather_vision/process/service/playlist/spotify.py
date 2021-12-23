from datetime import datetime
from typing import Optional, Iterable
from zoneinfo import ZoneInfo

from requests import codes

from gather_vision.process import item as app_items
from gather_vision import models as app_models
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.component.spotify_client import SpotifyClient
from gather_vision.process.service.playlist import abstract as service_mixins


class Spotify(
    service_mixins.PlaylistDetails,
    service_mixins.AuthRequiredService,
    service_mixins.PlaylistSource,
    service_mixins.PlaylistTarget,
):
    """Retrieve and set playlists for the Spotify music streaming service."""

    @property
    def code(self):
        return "spotify"

    @property
    def title(self):
        return "Spotify"

    @property
    def collections(self):
        return []

    def __init__(
        self,
        logger: Logger,
        http_client: HttpClient,
        normalise: Normalise,
        tz: ZoneInfo,
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

    def get_playlist(self, identifier: str, name: str, title: str):
        # get playlist details
        status, content = self._client.playlist_get(
            access_token=self._access_token,
            playlist_id=identifier,
            market=self._market,
        )
        playlist = app_items.Playlist(name=name, title=content.get("name"))
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
        self._logger.info("Retrieving tracks for Spotify playlist.")

        playlist = self.get_playlist(identifier, name, "")

        # get playlist tracks
        status, content = self._client.playlist_tracks_get(
            access_token=self._access_token,
            playlist_id=identifier,
            limit=limit,
            offset=0,
            market=self._market,
        )
        for index, track in enumerate(content.get("items", [])):
            track_number = index + 1
            item = track.get("track", {})
            track = self._build_track(name, track_number, item)
            playlist.tracks.append(track)
        return playlist

    def set_playlist_tracks(
        self,
        identifier: str,
        new_tracks: Iterable[app_items.Track],
        old_tracks: Iterable[app_items.Track],
    ):
        self._logger.info(f"Setting new tracks for Spotify playlist '{identifier}'.")
        song_ids = [t.track_id for t in new_tracks]
        status, content = self._client.playlist_tracks_set(
            access_token=self._access_token,
            playlist_id=identifier,
            song_ids=song_ids,
        )
        return status == codes.created

    def set_playlist_details(
        self,
        collection_name: str,
        playlist_id: str,
        title: str = None,
        description: str = None,
        is_public: bool = None,
    ):
        self._logger.info(f"Setting details for Spotify playlist '{collection_name}'.")
        status, content = self._client.playlist_details_set(
            access_token=self._access_token,
            playlist_id=playlist_id,
            title=title,
            description=description,
            is_public=is_public,
        )
        return status == codes.ok

    def search_tracks(
        self, playlist_name: str, track: str, artists: list[str], limit: int = 5
    ):
        query_status, query_result = self._client.track_query_get(
            access_token=self._access_token,
            query=f"{' '.join(artists)} {track}",
            limit=limit,
        )
        track_hits = query_result.get("tracks", {}).get("items", [])

        # stop if there are no results
        if not query_result or not track_hits:
            self._logger.warning(
                f"No match for {self.code} track matching "
                f"'{playlist_name}': '{track}' - '{artists}'."
            )
            return []

        tracks = []
        for index, item in enumerate(track_hits):
            track_number = index + 1
            track = self._build_track(playlist_name, track_number, item)
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

    def get_model_track(
        self, info: app_models.InformationSource, track: app_items.Track
    ):
        if not info or not track or not track.raw:
            raise ValueError(f"Cannot build playlist track from '{info}' '{track}'.")

        code = track.raw.get("id", "")
        title = track.raw.get("name", "")
        artists = ", ".join(
            [
                i.get("name", "")
                for i in track.raw.get("artists", [])
                if i.get("name", "")
            ]
        )
        info_url = next(
            (
                i
                for i in [
                    track.raw.get("href", "").strip(),
                    track.raw.get("external_urls", {}).get("spotify", "").strip(),
                ]
                if i
            ),
            "",
        )
        images = track.raw.get("album", {}).get("images", [])
        image_urls = sorted(images, reverse=True, key=lambda x: x.get("width"))
        image_url = next((i.get("url") for i in image_urls if self._valid_url(i)), "")

        obj, created = app_models.PlaylistTrack.objects.update_or_create(
            source=info,
            code=code,
            defaults={
                "title": title,
                "artists": artists,
                "info_url": info_url,
                "image_url": image_url,
                "musicbrainz_code": None,
            },
        )
        return obj

    def _build_track(
        self,
        collection_name: str,
        track_number: int,
        item: dict,
    ) -> app_items.Track:
        track_id = item.get("id")
        track_name = item.get("name")
        track_artists = [a.get("name") for a in item.get("artists")]

        (
            title_norm,
            primary_artists_norm,
            featured_artists_norm,
            queries,
        ) = self._normalise.track(track_name, track_artists, [])

        track = app_items.Track(
            service_name=self.code,
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

    def _valid_url(self, item: dict):
        image_max = 600
        return all(
            [
                item,
                item.get("url"),
                item.get("width") < image_max,
                item.get("height") < image_max,
            ]
        )
