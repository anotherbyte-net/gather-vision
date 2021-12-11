from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from django.utils.text import slugify

from gather_vision import models as app_models
from gather_vision.process import item as app_items
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.service.abstract import PlaylistSource


class Radio4zzz(PlaylistSource):
    """Get playlists from Radio 4zzz."""

    service_name = "radio4zzz"
    service_title = "Radio 4zzz"
    collection_names = ["most_played"]
    collection_titles = ["Most Played"]

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

        self._url_programs = "https://airnet.org.au/rest/stations/4ZZZ/programs"

        self._collection_config = {
            "most_played": self.build_most_played,
        }
        self._collection_name_title = dict(
            zip(self.collection_names, self.collection_titles)
        )

    def get_playlist(
        self,
        identifier: str,
        name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ):
        if name not in self._collection_config:
            raise ValueError(f"Unrecognised collection name '{name}'.")

        # set the limit
        if not limit:
            limit = 100
        elif limit < 1:
            limit = 1

        # construct the time span (1 week)
        current_time = datetime.now(tz=self._tz)
        if not start_date and not end_date:
            start_date = current_time - timedelta(days=8)
            end_date = current_time - timedelta(days=1)
        elif start_date and not end_date:
            end_date = start_date + timedelta(days=7)
        elif not start_date and end_date:
            start_date = end_date - timedelta(days=7)

        # download the tracks
        self._logger.info(
            f"Downloading up to {limit} tracks "
            f"from '{self.service_name}' collection '{name}'."
        )

        # first collect the tracks
        tracks = {}

        # programs
        for program in self.get_programs():
            program_url = program.get("programRestUrl")
            program_archived = program.get("archived") or False

            if program_archived:
                continue

            # episodes
            for episode in self.get_episodes(program_url, start_date, end_date):
                episode_url = episode.get("episodeRestUrl")

                # tracks
                for track in self.get_tracks(episode_url):
                    track_key = track.get("key")
                    track["program_info"] = program
                    track["episode_info"] = episode

                    if track_key in tracks:
                        tracks[track_key].append(track)
                    else:
                        tracks[track_key] = [track]

        playlist = self._collection_config[name](tracks, limit)
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

    def get_programs(self):
        data = self._http_client.get(self._url_programs)
        return data.json()

    def get_episodes(self, program_url: str, start_date: datetime, end_date: datetime):
        tz = self._tz
        url = f"{program_url}/episodes"
        data = self._http_client.get(url)
        episodes = data.json() or []
        for episode in episodes:
            episode_start = self._normalise.parse_date(episode.get("start", ""), tz)
            episode_end = self._normalise.parse_date(episode.get("end", ""), tz)

            # must be fully inside the from -> to dates
            if episode_start < start_date or episode_end > end_date:
                continue

            episode["start_date"] = episode_start
            episode["end_date"] = episode_end

            yield episode

    def get_tracks(self, episode_url: str):
        url = f"{episode_url}/playlists"
        data = self._http_client.get(url)
        tracks = data.json() or []
        for track in tracks:
            track_type = track.get("type")
            track_artist = track.get("artist")
            track_title = track.get("title")
            track_track = track.get("track")

            if track_type != "track":
                raise ValueError(
                    f"Track type is expected to be 'track', but is {track_type}."
                )

            if track_title != track_track:
                raise ValueError(
                    "Title and track are expected to match, "
                    f"but do not: '{track_title}' != '{track_track}'"
                )

            track_key = "-".join([slugify(track_artist), slugify(track_track)])
            track["key"] = track_key

            yield track

    def build_most_played(self, tracks, limit: int):
        name = "most_played"

        # find the top {limit} most played tracks
        most_played_tracks = sorted(
            [(len(v), k, v) for k, v in tracks.items()], reverse=True
        )[:limit]

        # build playlist
        title = self._collection_name_title[name]
        playlist = app_items.Playlist(
            name=f"{self.service_name}_{name}",
            title=f"{self.service_title} {title}",
        )
        for index, item in enumerate(most_played_tracks):
            track_number = index + 1
            play_count = item[0]
            track_key = item[1]
            track_infos = item[2]

            info = {"play_count": play_count}

            for track_info in track_infos:
                # program
                program = track_info.get("program_info", {})
                self._i(info, program, "program", "slug")
                self._i(info, program, "program", "broadcasters")
                self._i(info, program, "program", "gridDescription")
                self._i(info, program, "program", "name")

                # episode
                episode = track_info.get("episode_info", {})
                self._i(info, episode, "ep", "url")
                self._i(info, episode, "ep", "start")
                self._i(info, episode, "ep", "end")
                self._i(info, episode, "ep", "duration")
                self._i(info, episode, "ep", "multipleEpsOnDay")
                self._i(info, episode, "ep", "title")
                self._i(info, episode, "ep", "description")
                self._i(info, episode, "ep", "currentEpisode")
                self._i(info, episode, "ep", "imageUrl")
                self._i(info, episode, "ep", "smallImageUrl")
                self._i(info, episode, "ep", "episodeRestUrl")
                self._i(info, episode, "ep", "start_date")
                self._i(info, episode, "ep", "end_date")

                # track
                self._i(info, track_info, "", "key")
                self._i(info, track_info, "", "type")
                self._i(info, track_info, "", "id")
                self._i(info, track_info, "", "artist")
                self._i(info, track_info, "", "title")
                self._i(info, track_info, "", "track")
                self._i(info, track_info, "", "release")
                self._i(info, track_info, "", "time")
                self._i(info, track_info, "", "notes")
                self._i(info, track_info, "", "twitterHandle")
                self._i(info, track_info, "", "wikipedia")
                self._i(info, track_info, "", "image")
                self._i(info, track_info, "", "video")
                self._i(info, track_info, "", "url")
                self._i(info, track_info, "", "approximateTime")
                self._i(info, track_info, "", "thispart")

                # track - content
                track_content = track_info.get("contentDescriptors", {})
                self._i(info, track_content, "track", "isAustralian")
                self._i(info, track_content, "track", "isLocal")
                self._i(info, track_content, "track", "isFemale")
                self._i(info, track_content, "track", "isIndigenous")
                self._i(info, track_content, "track", "isNew")

                # track - testing
                track_testing = track_info.get("testing")
                self._i(info, track_testing, "track_test", "date")
                self._i(info, track_testing, "track_test", "timezone_type")
                self._i(info, track_testing, "track_test", "timezone")

            track_track = list(info.get("track", []))
            track_track = track_track[0] if len(track_track) == 1 else ""

            track_artists = list(info.get("artist", []))
            track_artists = track_artists[0] if len(track_artists) == 1 else ""

            # normalise title and artists
            (
                title_norm,
                primary_artists_norm,
                featured_artists_norm,
                queries,
            ) = self._normalise.track(track_track, track_artists, [])

            # add track to playlist
            playlist.add_track(
                service_name=self.service_name,
                collection_name=name,
                track_number=track_number,
                track_id=track_key,
                title=title_norm,
                primary_artists=primary_artists_norm,
                featured_artists=featured_artists_norm,
                queries=queries,
                raw=info,
            )
        return playlist

    def _i(self, container: dict, raw_container: dict, prefix: str, key: str) -> None:
        if not container or not raw_container or not key:
            return

        value = raw_container.get(key) or ""
        value = str(value)
        if not value or not value.strip():
            return

        container_key = f"{prefix}-{key}" if prefix else key

        if container_key not in container:
            container[container_key] = set()
        container[container_key].add(value)
