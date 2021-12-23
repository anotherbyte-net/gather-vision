from datetime import timedelta
from enum import Enum


class AvailableExpirationTime(Enum):
    """
    Enumeration of available cache times.

    - NEVER_EXPIRE - cache without expiry (i.e. keep)
    - DONT_CACHE - don't cache at all
    - others are the given time period
    """

    NEVER_EXPIRE = "never-expire"
    DONT_CACHE = "dont-cache"
    FIVE_MINUTES = timedelta(minutes=5)
    TEN_MINUTES = timedelta(minutes=10)
    THIRTY_MINUTES = timedelta(minutes=30)
    ONE_DAY = timedelta(days=1)
    ONE_WEEK = timedelta(weeks=1)
    ONE_MONTH = timedelta(weeks=4)

    def to_django_cache_value(self):
        """Get the cache timeout in seconds."""
        if self == AvailableExpirationTime.DONT_CACHE:
            # A timeout of 0 won't cache the value.
            return 0

        if self == AvailableExpirationTime.NEVER_EXPIRE:
            # Passing in None for timeout will cache the value forever.
            return None

        # django built-in cache needs the numbers of seconds for cache timeout
        return self.value.seconds

    def to_requests_cache_value(self):
        """Get the cache timeout value."""
        if self == AvailableExpirationTime.DONT_CACHE:
            # DO_NOT_CACHE = 0
            return 0

        if self == AvailableExpirationTime.NEVER_EXPIRE:
            # Never expire = None
            return None

        return self.value
