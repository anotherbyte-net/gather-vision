import os
from datetime import datetime, timedelta
from typing import Union
from zoneinfo import ZoneInfo

from django.utils import timezone

from gather_vision import models as app_models
from gather_vision.process import item as app_items
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.service.abc_radio import AbcRadio
from gather_vision.process.service.last_fm import LastFm
from gather_vision.process.service.radio_4zzz import Radio4zzz
from gather_vision.process.service.spotify import Spotify
from gather_vision.process.service.youtube_music import (
    YoutubeMusic,
)


class Playlists:
    def __init__(self, logger: Logger, tz: ZoneInfo):
        http_client = HttpClient(
            logger, use_cache=True, cache_expire=timedelta(minutes=10)
        )
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

        # self.init_spotify()
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

        # create info sources
        self.create_information_sources()

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

            for playlist_name_suffix in playlist_names_suffix:
                playlist = playlist_class.get_playlist(
                    playlist_name_suffix,
                    playlist_name_suffix,
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
                    self.update_playlist(
                        streaming_class, playlist_id, playlist_class, playlist
                    )

        self._logger.info("Finished updating playlists.")

    def update_playlist(
        self,
        streaming_class: Union[Spotify, YoutubeMusic],
        playlist_id: str,
        playlist_class: Union[AbcRadio, LastFm, Radio4zzz],
        playlist: app_items.Playlist,
    ):
        retrieved_date = timezone.now()

        # get the playlist item for the retrieved playlist
        source_model = app_models.InformationSource.objects.get(name=playlist.name)
        service_model = app_models.InformationSource.objects.get(
            name=streaming_class.service_name
        )
        (
            playlist_model,
            playlist_created,
        ) = app_models.PlaylistItem.objects.get_or_create(
            source=source_model, defaults={"retrieved_date": retrieved_date}
        )

        # get the tracks
        old_tracks_model = list(
            app_models.PlaylistTrack.objects.filter(
                source__name=playlist.name, entries__playlist=playlist_model
            ).prefetch_related("source", "entries")
        )
        old_tracks_service = streaming_class.get_playlist(playlist_id, playlist.name)
        new_tracks_source = playlist.tracks

        # assess the tracks
        old_track_model_matches = []
        old_track_service_matches = []
        for new_track_source in new_tracks_source:
            # model
            old_track_model = [
                i for i in old_tracks_model if new_track_source.matches_model(i)
            ]
            if len(old_track_model) > 1:
                raise ValueError([new_track_source, old_track_model])
            if old_track_model:
                old_track_model = old_track_model[0]
                old_track_model_matches.append(old_track_model)
            else:
                old_track_model = None

            # service
            old_track_service = [
                i
                for i in old_tracks_service.tracks
                if new_track_source.matches_track_title_artists(i)
            ]
            if len(old_track_service) > 1:
                raise ValueError([new_track_source, old_track_service])
            elif old_track_service:
                old_track_service = old_track_service[0]
                old_track_service_matches.append(old_track_service)
            else:
                old_track_service = self.select_service_track(
                    streaming_class, new_track_source
                )

            # store
            self.create_playlist_entry(
                playlist=playlist_model,
                new_track_source=new_track_source,
                new_playlist_track_source=playlist_class.get_model_track(
                    source_model, new_track_source
                ),
                old_playlist_track_source=old_track_model,
                old_track_service=old_track_service,
                new_playlist_track_service=streaming_class.get_model_track(
                    service_model, old_track_service
                ),
            )

        # old tracks that didn't match
        for old_track_model in old_tracks_model:
            if old_track_model not in old_track_model_matches:
                pass

        for old_track_service in old_tracks_service.tracks:
            if old_track_service not in old_track_service_matches:
                self._logger.warning(
                    f"Did not find '{old_track_service}' "
                    f"in '{streaming_class.service_name}'."
                )

        return None

    def select_service_track(
        self,
        streaming_class: Union[Spotify, YoutubeMusic],
        new_track_source: app_items.Track,
    ):
        for artists in new_track_source.iter_artists:
            tracks_service = streaming_class.search_tracks(
                playlist_name=new_track_source.collection_name,
                track=new_track_source.title,
                artists=artists,
            )
            # compare all artist
            for track_service in tracks_service:
                if new_track_source.matches_track_title_artists(track_service):
                    return track_service
        return None

    def create_information_sources(self):
        # playlist sources
        raw = [
            (Radio4zzz, "https://4zzz.org.au/"),
            (AbcRadio, "https://www.abc.net.au/triplej/"),
            (LastFm, "https://www.last.fm/"),
        ]
        for service, url in raw:
            for coll_name, coll_title in zip(
                service.collection_names, service.collection_titles
            ):
                name = "_".join([service.service_name, coll_name])
                title = " ".join([service.service_title, coll_title])
                app_models.InformationSource.objects.update_or_create(
                    name=name,
                    defaults={
                        "title": title,
                        "info_url": url,
                    },
                )

        # streaming services
        raw = [
            (Spotify, "https://www.spotify.com/"),
            (YoutubeMusic, "https://music.youtube.com/"),
        ]
        for service, url in raw:
            app_models.InformationSource.objects.update_or_create(
                name=service.service_name,
                defaults={
                    "title": service.service_title,
                    "info_url": url,
                },
            )

    def create_playlist_entry(
        self,
        playlist: app_models.PlaylistItem,
        new_track_source: app_items.Track,
        old_track_service: app_items.Track,
        new_playlist_track_source: app_models.PlaylistTrack,
        old_playlist_track_source: app_models.PlaylistTrack,
        new_playlist_track_service: app_models.PlaylistTrack,
    ):

        find_track = old_playlist_track_source
        if not find_track:
            find_track = new_playlist_track_source
        if not find_track:
            raise ValueError("No track information.")

        try:
            entry = app_models.PlaylistEntry.objects.get(
                playlist=playlist, tracks__pk=find_track.pk
            )

            if entry.position and new_track_source.track_number:
                entry.position_change = entry.position - new_track_source.track_number

            if new_track_source.track_number:
                entry.position = new_track_source.track_number

            entry.save()

        except app_models.PlaylistEntry.DoesNotExist:
            entry = app_models.PlaylistEntry(
                playlist=playlist, position=new_track_source.track_number
            )
            entry.save()

        entry.tracks.add(new_playlist_track_source)
        entry.tracks.add(new_playlist_track_service)

    def _get_env_var(self, key: str):
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Could not retrieve value for env var '{key}'.")
        return value

    def _build_env_var(self, name: str):
        return (name or "").casefold().upper()
