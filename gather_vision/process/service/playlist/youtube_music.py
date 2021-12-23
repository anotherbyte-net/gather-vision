from datetime import datetime
from typing import Optional, Iterable
from zoneinfo import ZoneInfo

from gather_vision.process import item as app_items
from gather_vision import models as app_models
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.component.youtube_music_client import (
    YoutubeMusicClient,
)
from gather_vision.process.service.playlist import abstract as service_mixins


class YoutubeMusic(
    service_mixins.PlaylistDetails,
    service_mixins.AuthRequiredService,
    service_mixins.PlaylistSource,
    service_mixins.PlaylistTarget,
):
    @property
    def code(self):
        return "ytmusic"

    @property
    def title(self):
        return "YouTube Music"

    @property
    def collections(self):
        return []

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

        self._client = YoutubeMusicClient(logger, http_client, tz)
        self._credentials: str = ""

    def get_playlist(self, identifier: str, name: str, title: str):
        playlist_raw = self._client.playlist_tracks_get(identifier, limit=1)
        playlist = app_items.Playlist(name=name, title=playlist_raw.get("title"))
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
        self._logger.info("Retrieving tracks for YouTube Music playlist.")
        playlist_raw = self._client.playlist_tracks_get(identifier, limit)

        playlist = app_items.Playlist(name=name, title=playlist_raw.get("title"))

        items = playlist_raw.get("tracks", [])
        for index, item in enumerate(items):
            track_number = index + 1
            track = self._build_track(name, track_number, item)
            playlist.tracks.append(track)
        return playlist

    def set_playlist_tracks(
        self,
        identifier: str,
        new_tracks: Iterable[app_items.Track],
        old_tracks: Iterable[app_items.Track],
    ):
        """Replace songs in a playlist."""
        msg = f"Setting new tracks for YouTube Music playlist '{identifier}'."
        self._logger.info(msg)
        return self._client.playlist_tracks_set(identifier, new_tracks, old_tracks)

    def set_playlist_details(
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

    def search_tracks(
        self, playlist_name: str, track: str, artists: list[str], limit: int = 5
    ):
        """Find matching tracks."""
        query_result = self._client.track_query_get(
            query=f"{track} {' '.join(artists)}",
            limit=limit,
        )

        # stop if there are no results
        if not query_result:
            self._logger.warning(
                f"No match for {self.code} track matching "
                f"'{playlist_name}': '{track}' - '{artists}'."
            )
            return []

        tracks = []
        for index, item in enumerate(query_result):
            track_number = index + 1
            track = self._build_track(playlist_name, track_number, item)
            tracks.append(track)
        return tracks

    def login_init(self):
        """Run the initial authorisation flow to get the credentials."""
        self._credentials = self._client.login_init()

    def login_next(self, credentials: str):
        """Get the next login token."""
        self._credentials = credentials
        self._client.login_token_next(credentials)

    def get_model_track(
        self, info: app_models.InformationSource, track: app_items.Track
    ):
        if not info or not track or not track.raw:
            raise ValueError(f"Cannot build playlist track from '{info}' '{track}'.")

        code = track.raw.get("videoId", "")
        title = track.raw.get("title", "")
        artists = ", ".join(
            [
                i.get("name", "")
                for i in track.raw.get("artists", [])
                if i.get("name", "")
            ]
        )
        info_url = "https://music.youtube.com/watch?v=" + code
        images = track.raw.get("thumbnails", [])
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
        track_id = item.get("videoId")
        track_title = item.get("title")
        track_artists = [a.get("name") for a in item.get("artists")]

        (
            title_norm,
            primary_artists_norm,
            featured_artists_norm,
            queries,
        ) = self._normalise.track(track_title, track_artists, [])

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
