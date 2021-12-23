from datetime import datetime, timedelta
from typing import Union, Iterable
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone

from gather_vision import models as app_models
from gather_vision.process import item as app_items
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.service.playlist import abstract as service_mixins
from gather_vision.process.service.playlist.abc_radio import AbcRadio
from gather_vision.process.service.playlist.abstract import (
    PlaylistDetails,
    PlaylistSource,
    PlaylistTarget,
)
from gather_vision.process.service.playlist.last_fm import LastFm
from gather_vision.process.service.playlist.radio_4zzz import Radio4zzz
from gather_vision.process.service.playlist.spotify import Spotify
from gather_vision.process.service.playlist.youtube_music import (
    YoutubeMusic,
)


class Playlists:
    def __init__(self, logger: Logger, tz: ZoneInfo, http_client: HttpClient):
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

        self._services: dict[
            str, Union[PlaylistDetails, PlaylistSource, PlaylistTarget]
        ] = dict(
            [
                (s.code, s)
                for s in [
                    self._spotify,
                    self._yt_music,
                    self._abc_radio,
                    self._last_fm,
                    self._radio_4zzz,
                ]
            ]
        )

    def run_init(self):
        self._logger.info("Initialising playlists.")

        # self.init_spotify()
        self.init_youtube_music()

        self._logger.info("Finished initialising playlists.")

    def init_spotify(self):
        client_id = settings.SPOTIFY_AUTH_CLIENT_ID
        client_secret = settings.SPOTIFY_AUTH_CLIENT_SECRET
        redirect_uri = settings.SPOTIFY_AUTH_REDIRECT_URI
        self._spotify.login_init(client_id, client_secret, redirect_uri)

    def init_youtube_music(self):
        self._yt_music.login_init()

    def run_update(self):
        self._logger.info("Updating playlists.")

        # create info sources
        self.create_information_sources()

        # login
        sp_client_id = settings.SPOTIFY_AUTH_CLIENT_ID
        sp_client_secret = settings.SPOTIFY_AUTH_CLIENT_SECRET
        sp_refresh_token = settings.SPOTIFY_AUTH_REFRESH_TOKEN
        self._spotify.login_next(sp_client_id, sp_client_secret, sp_refresh_token)

        ym_config = settings.YOUTUBE_MUSIC_AUTH_CONFIG
        self._yt_music.login_next(ym_config)

        lf_api_key = settings.LASTFM_AUTH_API_KEY
        self._last_fm.login_next(lf_api_key)

        # record when retrieval was performed
        retrieved_date = timezone.now()

        # don't update recently changed playlist entries, source tracks, and
        # streaming service tracks
        playlist_entries_time = 3
        playlist_entries_age = retrieved_date - timedelta(hours=playlist_entries_time)

        # build parameters
        current_time = datetime.now(tz=self._tz)
        start_date = current_time - timedelta(days=8)
        end_date = current_time - timedelta(days=1)
        limit = 100

        # for each playlist source
        playlist_settings = settings.PLAYLIST_SOURCES_TARGETS
        for playlist_setting in playlist_settings:
            source_service: PlaylistSource = self._services.get(
                playlist_setting.source_code
            )
            source_collection = playlist_setting.source_collection

            target_service: PlaylistTarget = self._services.get(
                playlist_setting.target_code
            )
            target_playlist_id = playlist_setting.target_playlist_id
            target_title = playlist_setting.target_title

            playlist = source_service.get_playlist_tracks(
                playlist_setting.source_code,
                source_collection,
                target_title,
                start_date,
                end_date,
                limit,
            )

            # create/update the playlist model
            source_model = app_models.InformationSource.objects.get(
                name=source_service.code
            )
            (
                playlist_model,
                playlist_created,
            ) = app_models.PlaylistItem.objects.update_or_create(
                source=source_model, defaults={"retrieved_date": retrieved_date}
            )
            old_tracks_model = list(
                app_models.PlaylistTrack.objects.filter(
                    source__name=playlist.name, entries__playlist=playlist_model
                ).prefetch_related("source", "entries")
            )
            new_tracks_source = playlist.tracks

            # update the playlist entries if they weren't recently updated
            # TODO: if not updating, then use the existing stored playlist entries / tracks from the source
            # Otherwise, the source might've been updated, and the streaming tracks won't match.
            if (
                not playlist_created
                and playlist_model.retrieved_date > playlist_entries_age
            ):
                self._logger.warning(
                    f"Not updating playlist '{playlist.name}' as it was "
                    f"last updated less than {playlist_entries_time} hours ago."
                )
            else:
                # update the playlist entries
                self.update_playlist_model(
                    source_model,
                    playlist_model,
                    source_service,
                    old_tracks_model,
                    new_tracks_source,
                )

            # update the streaming service tracks
            self.update_playlist_tracks(
                playlist_model,
                playlist,
                target_service,
                target_playlist_id,
                new_tracks_source,
            )

        self._logger.info("Finished updating playlists.")

    def create_information_sources(self):
        # playlist sources
        raw = [
            (self._radio_4zzz, "https://4zzz.org.au/"),
            (self._abc_radio, "https://www.abc.net.au/triplej/"),
            (self._last_fm, "https://www.last.fm/"),
        ]
        for service, url in raw:
            app_models.InformationSource.objects.update_or_create(
                name=service.code,
                defaults={
                    "title": service.title,
                    "info_url": url,
                },
            )

        # streaming services
        raw = [
            (self._spotify, "https://www.spotify.com/"),
            (self._yt_music, "https://music.youtube.com/"),
        ]
        for service, url in raw:
            app_models.InformationSource.objects.update_or_create(
                name=service.code,
                defaults={
                    "title": service.title,
                    "info_url": url,
                },
            )

    def update_playlist_model(
        self,
        source_model: app_models.InformationSource,
        playlist_model: app_models.PlaylistItem,
        playlist_service: Union[
            service_mixins.PlaylistSource, service_mixins.PlaylistDetails
        ],
        old_tracks_model: Iterable[app_models.PlaylistTrack],
        new_tracks_source: Iterable[app_items.Track],
    ):
        """Update the stored playlist entries and source tracks."""

        # for each new playlist entry
        new_entries = []
        for new_track_source in new_tracks_source:
            # check if there is a matching existing playlist entry
            old_track_model = [
                i for i in old_tracks_model if new_track_source.matches_model(i)
            ]
            if len(old_track_model) > 1:
                raise ValueError([new_track_source, old_track_model])

            entry = None
            if old_track_model:
                old_track_model = old_track_model[0]
                try:
                    entry = app_models.PlaylistEntry.objects.get(
                        playlist=playlist_model, tracks__pk=old_track_model.pk
                    )
                    if entry.position and new_track_source.track_number:
                        entry.position_change = (
                            entry.position - new_track_source.track_number
                        )
                    if new_track_source.track_number:
                        entry.position = new_track_source.track_number

                except app_models.PlaylistEntry.DoesNotExist:
                    pass

            # create/update the model for the new track
            new_playlist_track_model = playlist_service.get_model_track(
                source_model, new_track_source
            )

            # build new playlist entry if none exists
            if not entry:
                entry = app_models.PlaylistEntry(
                    playlist=playlist_model, position=new_track_source.track_number
                )

            new_entries.append((entry, new_playlist_track_model))

        # delete the current entries in the database for this playlist
        delete_result = app_models.PlaylistEntry.objects.filter(
            playlist=playlist_model
        ).delete()
        self._logger.info(f"Deleted old entries: {delete_result}.")

        # save the new entries and tracks for this playlist
        for new_entry, new_entry_track in new_entries:
            new_entry.save()
            new_entry.tracks.add(new_entry_track)
        self._logger.info(f"Created {len(new_entries)} new playlist entries.")

    def update_playlist_tracks(
        self,
        playlist_model: app_models.PlaylistItem,
        playlist_source: app_items.Playlist,
        streaming_service: Union[
            service_mixins.PlaylistDetails,
            service_mixins.PlaylistTarget,
            service_mixins.PlaylistSource,
        ],
        playlist_service_id: str,
        new_tracks_source: Iterable[app_items.Track],
    ):
        """Update the stored playlist tracks from a streaming service."""

        # get the streaming service information
        service_model = app_models.InformationSource.objects.get(
            name=streaming_service.code
        )
        old_tracks_service = streaming_service.get_playlist_tracks(
            playlist_service_id, playlist_source.name
        )

        # assess the tracks and build the models
        new_entries = []
        old_track_service_matches = []
        for new_track_source in new_tracks_source:
            try:
                entry = app_models.PlaylistEntry.objects.get(
                    playlist=playlist_model, tracks__code=new_track_source.track_id
                )
            except app_models.PlaylistEntry.DoesNotExist:
                a = 1

            # service
            track_service = [
                i
                for i in old_tracks_service.tracks
                if new_track_source.matches_track_title_artists(i)
            ]
            if len(track_service) > 1:
                raise ValueError([new_track_source, track_service])
            elif track_service:
                track_service = track_service[0]
                old_track_service_matches.append(track_service)
            else:
                track_service = self.select_service_track(
                    streaming_service, new_track_source
                )

            # create/update the model for the new track
            if track_service:
                new_playlist_track_model = streaming_service.get_model_track(
                    service_model, track_service
                )

                # store
                new_entries.append((entry, new_playlist_track_model))

        # tracks that didn't match
        for old_track_service in old_tracks_service.tracks:
            if old_track_service not in old_track_service_matches:
                self._logger.warning(
                    f"Did not find '{old_track_service}' "
                    f"in '{streaming_service.code}'."
                )

        # save the new entries and tracks for this playlist
        for new_entry, new_entry_track in new_entries:
            new_entry.tracks.add(new_entry_track)
        self._logger.info(f"Created {len(new_entries)} new playlist entries.")

        return None

    def select_service_track(
        self,
        streaming_service: service_mixins.PlaylistTarget,
        new_track_source: app_items.Track,
    ):
        for artists in new_track_source.iter_artists:
            tracks_service = streaming_service.search_tracks(
                playlist_name=new_track_source.collection_name,
                track=new_track_source.title,
                artists=artists,
            )
            # compare all artist
            for track_service in tracks_service:
                if new_track_source.matches_track_title_artists(track_service):
                    return track_service
        return None

    def _build_streaming_service_identifier(
        self, playlist_code: str, playlist_collection: str
    ):
        return "_".join([playlist_code, playlist_collection]).casefold().upper()
