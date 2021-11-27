import uuid

import pytz
import requests_mock
from django.test import TestCase

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.normalise import Normalise
from gather_vision.process.service.radio_4zzz import Radio4zzz


class TestPlaylistsComponentRadio4zzz(TestCase):
    def setUp(self) -> None:
        logger = Logger()
        tz = pytz.timezone("Australia/Brisbane")
        normalise = Normalise()
        api_key = f"api_key-{uuid.uuid4()}"

        http_client = HttpClient(logger, use_cache=False)

        self._logger = logger
        self._normalise = normalise
        self._http_client = http_client
        self._api_key = api_key
        self._tz = tz

        self._service = Radio4zzz(logger, http_client, normalise, tz)

    def test_get_playlist(self):
        # arrange
        service_name = "radio4zzz"
        collection_name = "most_played"
        limit = 100

        track_title = "title"
        artist1 = f"artist1-{uuid.uuid4()}".replace("-", " ")
        artist2 = f"artist2-{uuid.uuid4()}".replace("-", " ")

        # act
        with requests_mock.Mocker() as m, self.assertLogs() as al:
            m.get("https://airnet.org.au/rest/stations/4ZZZ/programs", json={})
            playlist = self._service.get_playlist(
                name=collection_name, title=track_title, limit=limit
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
