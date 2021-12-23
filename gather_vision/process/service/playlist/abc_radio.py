from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from gather_vision import models as app_models
from gather_vision.process import item as app_items
from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.service.playlist import abstract as service_mixins


class AbcRadio(service_mixins.PlaylistDetails, service_mixins.PlaylistSource):
    """Get playlists from ABC Radio."""

    @property
    def code(self):
        return "abcradio"

    @property
    def title(self):
        return "ABC Radio"

    @property
    def collections(self):
        return ["doublej_most_played", "triplej_most_played", "unearthed_most_played"]

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

        self._url = "https://music.abcradio.net.au/api/v1/recordings/plays.json"

        self._collection_config = {
            "doublej_most_played": "doublej",
            "triplej_most_played": "triplej",
            "unearthed_most_played": "unearthed",
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

        # construct the time span (1 week)
        current_time = datetime.now(tz=self._tz)
        current_day = current_time.date()
        if not start_date and not end_date:
            start_date = current_day - timedelta(days=8)
            end_date = current_day - timedelta(days=1)
        elif start_date and not end_date:
            end_date = start_date + timedelta(days=7)
        elif not start_date and end_date:
            start_date = end_date - timedelta(days=7)

        # build the url
        url_name = self._collection_config[name]
        qs = self.build_qs(
            name=url_name,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

        # download the tracks
        self._logger.info(
            f"Downloading up to {limit} tracks "
            f"from '{self.code}' collection '{name}'."
        )
        data = self._http_client.get(self._url, params=qs)

        # build the playlist
        playlist = self.get_playlist(identifier, name, title)
        for index, item in enumerate(data.json()["items"]):
            track_number = index + 1
            track_title = item["title"]
            track_id = item["arid"]
            original_artists = item["artists"]

            # get primary artist and featured artists
            sep = self._normalise.track_sep_spaced
            primary_artists = ""
            featured_artists = ""
            for raw_artist in original_artists:
                artist_type = raw_artist["type"]
                artist_name = raw_artist["name"]

                if artist_type == "primary":
                    primary_artists = f"{primary_artists}{sep} {artist_name}"

                elif artist_type == "featured":
                    featured_artists = f"{featured_artists}{sep} {artist_name}"

                else:
                    raise Exception(
                        f"Unrecognised artist '{artist_name}' ({artist_type})."
                    )

            # normalise title and artists
            (
                title_norm,
                primary_artists_norm,
                featured_artists_norm,
                queries,
            ) = self._normalise.track(track_title, primary_artists, featured_artists)

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

    def build_qs(
        self,
        name: str,
        start_date: datetime,
        end_date: datetime,
        order: str = "desc",
        limit: int = 50,
    ) -> dict:

        if not name:
            raise ValueError("Must provide name.")
        if not start_date:
            raise ValueError("Must provide start date.")
        if not end_date:
            raise ValueError("Must provide end date.")
        if not order or order not in ["desc", "asc"]:
            raise ValueError("Must provide order, one of 'desc' or 'asc'.")
        if not limit or limit < 1:
            raise ValueError("Must provide limit greater than 0.")

        qs = {
            "order": order,
            "limit": limit,
            "service": name,
            "from": f"{start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}",
            "to": f"{end_date.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        }
        return qs

    def get_model_track(
        self,
        info: app_models.InformationSource,
        track: app_items.Track,
    ):
        if not info or not track or not track.raw:
            raise ValueError(
                f"Cannot build spotify playlist track from '{info}' '{track}'."
            )

        code = track.raw.get("arid", "")
        title = track.raw.get("title", "")
        artists = ", ".join(
            [
                i.get("name", "")
                for i in track.raw.get("artists", [])
                if i.get("name", "")
            ]
        )

        urls1 = track.raw.get("links", [])
        urls2 = [j for i in track.raw.get("releases", []) for j in i.get("links", [])]
        urls3 = [j for i in track.raw.get("artists", []) for j in i.get("links", [])]
        urls = urls1 + urls2 + urls3
        info_url = next(
            (i.get("url") for i in urls if i and "musicbrainz" not in i.get("url")), ""
        )

        images = [
            j for i in track.raw.get("releases", []) for j in i.get("artwork", [])
        ] + track.raw.get("artwork", [])

        image_urls = sorted(images, reverse=True, key=lambda x: x.get("width"))
        image_url = next((i.get("url") for i in image_urls if self._valid_url(i)), "")

        musicbrainz_links = track.raw.get("links", []) + [
            j for i in track.raw.get("releases", []) for j in i.get("links", [])
        ]
        musicbrainz_code = next(
            (
                i.get("id_component")
                for i in musicbrainz_links
                if i and "musicbrainz" in i.get("url")
            ),
            None,
        )

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
