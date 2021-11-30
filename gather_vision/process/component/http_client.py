from datetime import timedelta

import requests
from requests import Session
from requests_cache import CachedSession

from gather_vision.process.component.logger import Logger


class HttpClient:
    def __init__(self, logger: Logger, use_cache: bool = True):
        self._logger = logger
        agent = "gather-vision (+https://github.com/anotherbyte-net/gather-vision)"
        self._headers = {"user-agent": agent}

        if use_cache:
            self._session = CachedSession(
                ".local/http_cache", backend="sqlite", expire_after=timedelta(days=1)
            )
            logger.debug(f"HTTP cache: {self._session.cache.db_path}")
        else:
            self._session = Session()

    def get(self, url: str, **kwargs):
        """HTTP GET"""
        if "headers" in kwargs:
            kwargs["headers"] = {**kwargs["headers"], **self._headers}

        result = self._session.get(url, **kwargs)
        if result.status_code != requests.codes.ok or not result.content:
            self._logger.warning(
                f"Response {result.status_code} '{result.reason}' "
                f"length {len(result.content)} for GET {url}"
            )
            return None
        return result

    def head(self, url: str):
        """HTTP HEAD"""
        result = self._session.head(url, headers=self._headers)
        if result.status_code != requests.codes.ok or not result.content:
            self._logger.warning(
                f"Response {result.status_code} '{result.reason}' "
                f"length {len(result.content)} for HEAD {url}"
            )
            return None
        return result

    def put(self, url: str, **kwargs):
        """HTTP PUT"""
        if "headers" in kwargs:
            kwargs["headers"] = {**kwargs["headers"], **self._headers}

        result = self._session.put(url, **kwargs)
        if result.status_code != requests.codes.ok or not result.content:
            self._logger.warning(
                f"Response {result.status_code} '{result.reason}' "
                f"length {len(result.content)} for PUT {url}"
            )
            return None
        return result

    def post(self, url: str, **kwargs):
        """HTTP POST"""
        if "headers" in kwargs:
            kwargs["headers"] = {**kwargs["headers"], **self._headers}

        result = self._session.post(url, **kwargs)
        if result.status_code != requests.codes.ok or not result.content:
            self._logger.warning(
                f"Response {result.status_code} '{result.reason}' "
                f"length {len(result.content)} for POST {url}"
            )
            return None
        return result
