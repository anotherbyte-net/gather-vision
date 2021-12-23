from importlib import import_module

from django.core import signals
from django.core.cache.backends.base import (
    InvalidCacheBackendError,
)
from django.utils.connection import BaseConnectionHandler, ConnectionProxy
from requests import Session
from requests_cache import CachedSession

__all__ = [
    "external_http_cache",
    "external_http_caches",
    "DEFAULT_EXTERNAL_HTTP_CACHE_ALIAS",
]

from gather_vision.process.cache.available_expiration_time import (
    AvailableExpirationTime,
)

DEFAULT_EXTERNAL_HTTP_CACHE_ALIAS = "default"


class ExternalHttpCacheHandler(BaseConnectionHandler):
    settings_name = "EXTERNAL_HTTP_CACHES"
    exception_class = InvalidCacheBackendError

    def create_connection(self, alias):
        params = self.settings[alias].copy()
        backend: str = params.pop("BACKEND", None)
        cache_name: str = params.pop("LOCATION", None)
        expires: str = params.pop("EXPIRES", None)
        backend_params: dict = params.pop("BACKEND_PARAMS", {})

        if backend is None:
            return Session()

        try:
            backend_package, backend_resource = backend.rsplit(".", maxsplit=1)
            backend_class = getattr(import_module(backend_package), backend_resource)
            backend_instance = backend_class(**backend_params)

            cache_obj = CachedSession(
                cache_name=cache_name,
                backend=backend_instance,
                cache_control=True,
                expire_after=AvailableExpirationTime[expires].to_requests_cache_value(),
                timeout=30,
            )
        except ImportError as e:
            msg = f"Could not find backend '{backend}': {e}"
            raise InvalidCacheBackendError(msg) from e

        return cache_obj

    def all(self, initialized_only=False):
        return [
            self[alias]
            for alias in self
            # If initialized_only is True, return only initialized caches.
            if not initialized_only or hasattr(self._connections, alias)
        ]


external_http_caches = ExternalHttpCacheHandler()

external_http_cache = ConnectionProxy(
    external_http_caches, DEFAULT_EXTERNAL_HTTP_CACHE_ALIAS
)


def close_external_http_caches(**kwargs):
    # Some caches need to do a cleanup at the end of a request cycle. If not
    # implemented in a particular backend cache.close() is a no-op.
    for item in external_http_caches.all(initialized_only=True):
        item.close()


signals.request_finished.connect(close_external_http_caches)
