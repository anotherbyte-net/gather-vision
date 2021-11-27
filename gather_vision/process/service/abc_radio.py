from datetime import tzinfo, datetime, timedelta
from string import Template
from typing import Optional
from urllib.parse import urlencode

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.item.playlist import Playlist


class AbcRadio:
    """Get playlists from ABC Radio."""

    service_name = "abcradio"
    service_title = "ABC Radio"
    collection_names = [
        "doublej_most_played",
        "triplej_most_played",
        "unearthed_most_played",
    ]
    collection_titles = [
        "Double J Most Played",
        "Triple J Most Played",
        "Unearthed Most Played",
    ]

    def __init__(
        self, logger: Logger, http_client: HttpClient, normalise: Normalise, tz: tzinfo
    ):
        self._logger = logger
        self._http_client = http_client
        self._normalise = normalise
        self._tz = tz

        self._url_template = Template(
            "https://music.abcradio.net.au/api/v1/recordings/plays.json?$qs"
        )
        self._collection_config = {
            "doublej_most_played": "doublej",
            "triplej_most_played": "triplej",
            "unearthed_most_played": "unearthed",
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
        url = self.build_url(
            name=url_name,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

        # download the tracks
        self._logger.info(
            f"Downloading up to {limit} tracks "
            f"from '{self.service_name}' collection '{name}'."
        )
        data = self._http_client.get(url)

        # build the playlist
        playlist = Playlist(
            name=f"{self.service_name}_{name}",
            title=f"{self.service_title} {title}",
        )
        for index, item in enumerate(data.json()["items"]):
            track_number = index + 1
            track_title = item["title"]
            track_id = item["arid"]
            original_artists = item["artists"]

            # get primary artist and featured artists
            sep = self._normalise.sep_spaced
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

    def build_url(
        self,
        name: str,
        start_date: datetime,
        end_date: datetime,
        order: str = "desc",
        limit: int = 50,
    ) -> str:

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

        qs = urlencode(
            {
                "order": order,
                "limit": limit,
                "service": name,
                "from": f"{start_date.strftime('%Y-%m-%dT%H:%M:%SZ')}",
                "to": f"{end_date.strftime('%Y-%m-%dT%H:%M:%SZ')}",
            }
        )
        url_str = self._url_template.substitute(qs=qs)
        return url_str
