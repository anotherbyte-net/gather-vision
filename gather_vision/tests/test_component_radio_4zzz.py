import uuid

import pytz
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
