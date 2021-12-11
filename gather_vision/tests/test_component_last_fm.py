import uuid

from zoneinfo import ZoneInfo
import requests_mock
from django.test import TestCase

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.service.last_fm import LastFm


class TestPlaylistsComponentLastFm(TestCase):
    def setUp(self) -> None:
        logger = Logger()
        tz = ZoneInfo("Australia/Brisbane")
        normalise = Normalise()
        api_key = f"api_key-{uuid.uuid4()}"
        http_client = HttpClient(logger, use_cache=False)

        self._logger = logger
        self._normalise = normalise
        self._http_client = http_client
        self._api_key = api_key
        self._tz = tz

        self._service = LastFm(logger, http_client, normalise, tz)
        self._service.login_next(api_key)

    def test_build_qs_missing(self):
        # arrange

        # act
        with self.assertRaises(ValueError) as ar:
            self._service.build_qs(None, None)

        # assert
        self.assertEqual(str(ar.exception), "Must provide method.")

    def test_build_url(self):
        # arrange

        method = f"method1-{uuid.uuid4()}"
        country = f"country1-{uuid.uuid4()}"
        order = "desc"
        limit = 20

        # act
        qs = self._service.build_qs(
            method=method,
            country=country,
            limit=limit,
        )

        # assert
        expected_qs = {
            "api_key": self._api_key,
            "method": method,
            "country": country,
            "format": "json",
            "limit": limit,
            "page": 1,
        }

        self.assertEqual(qs, expected_qs)

    def test_get_playlist(self):
        # arrange
        service_name = "lastfm"
        collection_name = "most_popular"
        limit = 20

        track_title = "title"
        track_arid = f"id-{uuid.uuid4()}"
        artist1 = f"artist1-{uuid.uuid4()}".replace("-", " ")
        artist2 = f"artist2-{uuid.uuid4()}".replace("-", " ")

        # act
        with requests_mock.Mocker() as m, self.assertLogs() as al:
            m.get(
                f"https://ws.audioscrobbler.com/2.0/?api_key={self._api_key}&method=geo.gettoptracks&country=australia&format=json&limit=20&page=1",
                json={
                    "tracks": {
                        "track": [
                            {
                                "name": track_title,
                                "url": track_arid,
                                "artist": {
                                    "name": f"{artist1}, {artist2}",
                                },
                            }
                        ]
                    }
                },
            )
            playlist = self._service.get_playlist(
                identifier=collection_name,
                name=collection_name,
                limit=limit,
            )

        # assert
        self.assertEqual(
            [str(i) for i in playlist.tracks],
            [f"{service_name}:{collection_name}:1:{artist1}:{track_title}"],
        )
        self.assertEqual(
            al.output,
            [
                f"INFO:root:Downloading up to {limit} tracks from '{service_name}' collection '{collection_name}'.",
                f"INFO:root:Retrieved 1 tracks from '{service_name}' collection '{collection_name}'.",
            ],
        )
        self.assertEqual(len(playlist.tracks), 1)
        self.assertEqual(
            str(playlist.tracks[0]),
            f"{service_name}:{collection_name}:1:{artist1}:{track_title}",
        )
