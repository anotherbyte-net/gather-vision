import uuid
from datetime import datetime, timedelta

from zoneinfo import ZoneInfo
import requests_mock
from django.test import TestCase

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.service.playlist.abc_radio import AbcRadio


class TestPlaylistsComponentAbcRadio(TestCase):
    def setUp(self) -> None:
        logger = Logger()
        tz = ZoneInfo("Australia/Brisbane")
        normalise = Normalise()
        http_client = HttpClient(logger)

        self._logger = logger
        self._normalise = normalise
        self._http_client = http_client
        self._tz = tz

        self._service = AbcRadio(logger, http_client, normalise, tz)

    def test_build_url_missing(self):
        # arrange

        # act
        with self.assertRaises(ValueError) as ar:
            self._service.build_qs(
                name=None, start_date=datetime.now(), end_date=datetime.now()
            )

        # assert
        self.assertEqual(str(ar.exception), "Must provide name.")

    def test_build_qs(self):
        # arrange
        collection_name = "testing"
        start = datetime.now() - timedelta(days=8)
        end = start + timedelta(days=7)
        order = "desc"
        limit = 20

        # act
        qs = self._service.build_qs(
            name=collection_name,
            start_date=start,
            end_date=end,
            order=order,
            limit=limit,
        )

        # assert
        expected_qs = {
            "order": order,
            "limit": limit,
            "service": collection_name,
            "from": f"{start.year:04}-{start.month:02}-{start.day:02}T"
            f"{start.hour:02}:{start.minute:02}:{start.second:02}Z",
            "to": f"{end.year:04}-{end.month:02}-{end.day:02}T"
            f"{end.hour:02}:{end.minute:02}:{end.second:02}Z",
        }
        self.assertEqual(qs, expected_qs)

    def test_get_playlist(self):
        # arrange
        service_name = "abcradio"
        collection_name = "doublej_most_played"
        collection_id = "doublej"
        start_date = datetime.now() - timedelta(days=8)
        end_date = start_date + timedelta(days=7)
        order = "desc"
        limit = 20
        self.maxDiff = None

        track_title = "title"
        track_arid = f"id-{uuid.uuid4()}"
        artist1 = f"artist1-{uuid.uuid4()}".replace("-", " ")
        artist2 = f"artist2-{uuid.uuid4()}".replace("-", " ")

        expected_url = (
            "https://music.abcradio.net.au/api/v1/recordings/plays.json?"
            + f"order={order}&limit={limit}&service={collection_id}&"
            + f"from={start_date.year:04}-{start_date.month:02}-{start_date.day:02}T"
            + f"{start_date.hour:02}%3A{start_date.minute:02}%3A{start_date.second:02}Z&"
            + f"to={end_date.year:04}-{end_date.month:02}-{end_date.day:02}T"
            + f"{end_date.hour:02}%3A{end_date.minute:02}%3A{end_date.second:02}Z"
        )

        # act
        with requests_mock.Mocker() as m, self.assertLogs() as al:
            m.get(
                expected_url,
                json={
                    "items": [
                        {
                            "title": track_title,
                            "arid": track_arid,
                            "artists": [
                                {"type": "primary", "name": artist1},
                                {"type": "featured", "name": artist2},
                            ],
                        }
                    ]
                },
            )

            playlist = self._service.get_playlist_tracks(
                identifier=collection_name,
                name=collection_name,
                start_date=start_date,
                end_date=end_date,
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
