from typing import Optional

import requests
from requests import Session

from gather_vision.process.cache.external_http_cache import external_http_caches
from gather_vision.process.component.logger import Logger
from gather_vision.process.component.metadata import Metadata


class HttpClient:
    def __init__(self, logger: Logger, cache_alias: Optional[str] = "default"):
        self._logger = logger
        self._metadata = Metadata()

        agent_url = self._metadata.documentation_url()
        agent = f"gather-vision (+{agent_url})"
        self._headers = {"user-agent": agent}
        self._logger.debug(f"User agent set to '{agent}'.")

        if cache_alias:
            self._session = external_http_caches[cache_alias]
            logger.debug(f"Using external http client cache '{cache_alias}'.")
        else:
            self._session = Session()
            logger.debug(f"Not using an external http client cache.")

    @property
    def session(self):
        return self._session

    def get(self, url: str, **kwargs):
        """HTTP GET"""
        return self._send_request("GET", url, **kwargs)

    def head(self, url: str, **kwargs):
        """HTTP HEAD"""
        return self._send_request("HEAD", url, **kwargs)

    def put(self, url: str, **kwargs):
        """HTTP PUT"""
        return self._send_request("PUT", url, **kwargs)

    def post(self, url: str, **kwargs):
        """HTTP POST"""
        return self._send_request("POST", url, **kwargs)

    def _send_request(self, method: str, url: str, **kwargs):
        """Send a request using the 'requests' library."""

        # Add default headers.
        # The default headers can be customised via the kwargs.
        kwargs["headers"] = {**self._headers, **kwargs.get("headers", {})}

        if "timeout" not in kwargs:
            # Set a default timeout.
            # Surprisingly, requests does not set a default timeout.
            # Requests only provides an easy way to set a timeout on individual requests.
            kwargs["timeout"] = 30

        result = self._session.request(method, url, **kwargs)

        if result.status_code != requests.codes.ok or not result.content:
            self._logger.warning(
                f"Response {result.status_code} '{result.reason}' "
                f"length {len(result.content)} for {method} {url}"
            )
            return None
        return result
