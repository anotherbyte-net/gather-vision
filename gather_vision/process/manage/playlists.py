import os
from datetime import datetime, timedelta
from typing import Union

import pytz

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.item.playlist import Playlist
from gather_vision.process.service.abc_radio import AbcRadio
from gather_vision.process.service.last_fm import LastFm
from gather_vision.process.service.radio_4zzz import Radio4zzz
from gather_vision.process.service.spotify import Spotify
from gather_vision.process.service.youtube_music import (
    YoutubeMusic,
)


class Playlists:
    def __init__(self, logger: Logger, tz: pytz.timezone):
        http_client = HttpClient(logger, use_cache=True)
        normalise = Normalise()

        spotify = Spotify(logger, http_client, normalise, tz)
        yt_music = YoutubeMusic(logger, http_client, normalise, tz)

        abc_radio = AbcRadio(logger, http_client, normalise, tz)
        last_fm = LastFm(logger, http_client, normalise, tz)
        radio_4zzz = Radio4zzz(logger, http_client, normalise, tz)

        self._logger = logger
        self._tz = tz

        self._http_client = http_client
        self._normalise = normalise

        self._spotify = spotify
        self._yt_music = yt_music

        self._abc_radio = abc_radio
        self._last_fm = last_fm
        self._radio_4zzz = radio_4zzz

    def init(self):
        self._logger.info("Initialising playlists.")

        self.init_spotify()
        self.init_youtube_music()

        self._logger.info("Finished initialising playlists.")

    def init_spotify(self):
        client_id = self._get_env_var(Spotify.key_client_id)
        client_secret = self._get_env_var(Spotify.key_client_secret)
        redirect_uri = self._get_env_var(Spotify.key_redirect_uri)
        self._spotify.login_init(client_id, client_secret, redirect_uri)

    def init_youtube_music(self):
        self._yt_music.login_init()

    def update_playlists(self):
        self._logger.info("Updating playlists.")

        # login
        sp_client_id = self._get_env_var(Spotify.key_client_id)
        sp_client_secret = self._get_env_var(Spotify.key_client_secret)
        sp_refresh_token = self._get_env_var(Spotify.key_refresh_token)
        self._spotify.login_next(sp_client_id, sp_client_secret, sp_refresh_token)

        ym_config = self._get_env_var(YoutubeMusic.key_config)
        self._yt_music.login_next(ym_config)

        lf_api_key = self._get_env_var(LastFm.key_api_key)
        self._last_fm.login_next(lf_api_key)

        # available playlist sources
        playlist_sources = [
            {
                "class": self._abc_radio,
                "name": self._abc_radio.service_name,
                "title": self._abc_radio.service_title,
                "coll_names": self._abc_radio.collection_names,
                "coll_titles": self._abc_radio.collection_titles,
            },
            {
                "class": self._last_fm,
                "name": self._last_fm.service_name,
                "title": self._last_fm.service_title,
                "coll_names": self._last_fm.collection_names,
                "coll_titles": self._last_fm.collection_titles,
            },
            {
                "class": self._radio_4zzz,
                "name": self._radio_4zzz.service_name,
                "title": self._radio_4zzz.service_title,
                "coll_names": self._radio_4zzz.collection_names,
                "coll_titles": self._radio_4zzz.collection_titles,
            },
        ]

        # available streaming services
        streaming_services = [
            {"class": self._spotify},
            {"class": self._yt_music},
        ]

        # build parameters
        current_time = datetime.now(tz=self._tz)
        start_date = current_time - timedelta(days=8)
        end_date = current_time - timedelta(days=1)
        limit = 100

        # create playlists
        for playlist_source in playlist_sources:
            playlist_class = playlist_source.get("class")
            playlist_names_suffix = playlist_source.get("coll_names")
            playlist_titles_suffix = playlist_source.get("coll_titles")

            for playlist_name_suffix, playlist_title_suffix in zip(
                playlist_names_suffix, playlist_titles_suffix
            ):
                playlist = playlist_class.get_playlist(
                    playlist_name_suffix,
                    playlist_title_suffix,
                    start_date,
                    end_date,
                    limit,
                )

                # update playlists
                for streaming_service in streaming_services:
                    streaming_class = streaming_service.get("class")

                    pi = "playlistid"
                    key = f"{streaming_class.service_name}_{pi}_{playlist.name}"
                    playlist_id = self._get_env_var(self._build_env_var(key))
                    self.update_playlist(streaming_class, playlist_id, playlist)

        self._logger.info("Finished updating playlists.")

    def update_playlist(
        self,
        streaming_class: Union[Spotify, YoutubeMusic],
        playlist_id: str,
        playlist: Playlist,
    ):
        old_tracks = streaming_class.playlist_tracks_get(playlist.name, playlist_id)
        new_tracks = playlist.tracks

        old_track_queries = dict([(q, i) for i in old_tracks for q in i.queries])
        new_track_queries = dict([(q, i) for i in new_tracks for q in i.queries])

        matches = set()
        old_misses = set()
        new_misses = set()
        for q, old_track in old_track_queries.items():
            new_track = new_track_queries.get(q)
            if new_track:
                matches.add(old_track)
            else:
                old_misses.add(old_track)

        for q, new_track in new_track_queries.items():
            old_track = old_track_queries.get(q)
            if old_track:
                matches.add(new_track)
            else:
                new_misses.add(new_track)

        # TODO
        # update_success = streaming_class.playlist_tracks_set(
        #     playlist.name, playlist_id, new_tracks, old_tracks
        # )
        # if not update_success:
        #     pass

        # streaming_class.playlist_details_set()
        raise NotImplementedError()

    def _get_env_var(self, key: str):
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Could not retrieve value for env var '{key}'.")
        return value

    def _build_env_var(self, name: str):
        return (name or "").casefold().upper()
