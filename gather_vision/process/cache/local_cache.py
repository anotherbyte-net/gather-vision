from typing import Optional, Any

from django.core.cache import caches

from gather_vision.process.cache.available_expiration_time import (
    AvailableExpirationTime,
)
from gather_vision.process.component.logger import Logger


class LocalCache:
    """A local cache."""

    def __init__(self, logger: Logger, cache_alias: Optional[str] = "default"):
        self._logger = logger
        self._cache_alias = cache_alias
        if cache_alias:
            self._cache = caches[cache_alias]
            self._logger.debug(f"Using local cache '{cache_alias}'.")
        else:
            self._cache = None
            self._logger.debug(f"Not using local cache.")

    def get(
        self, key: str, default=None, version: Optional[int] = None
    ) -> tuple[bool, Any]:
        """Retrieve a value from the cache."""
        if self._cache is None:
            return False, None

        # If the literal value None can be stored in the cache,
        # use a sentinel object as the default
        # to determine whether the object exists in the cache.
        sentinel = object()
        result = self._cache.get(
            key=key,
            default=sentinel if default is None else default,
            version=version,
        )
        if result is sentinel:
            return False, None
        return True, result

    def set(
        self,
        key: str,
        value: Any,
        cache_time: AvailableExpirationTime = AvailableExpirationTime.NEVER_EXPIRE,
        version: Optional[int] = None,
    ) -> None:
        """Store a value in the cache."""
        if self._cache is None:
            return

        self._cache.set(
            key=key,
            value=value,
            timeout=cache_time.to_django_cache_value(),
            version=version,
        )

    def get_or_set(
        self,
        key: str,
        value: Any,
        cache_time: AvailableExpirationTime = AvailableExpirationTime.NEVER_EXPIRE,
        version: Optional[int] = None,
    ) -> Any:
        """Store a value if there is no existing value, then retrieve the value."""
        if self._cache is None:
            return None

        return self._cache.get_or_set(
            key=key,
            default=value,
            timeout=cache_time.to_django_cache_value(),
            version=version,
        )

    def clear(self):
        """Empty the cache."""
        if self._cache:
            self._cache.clear()
