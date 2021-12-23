from gather_vision.process.component.logger import Logger

from enum import Enum
from typing import Optional, Any

from django.core.cache import caches


class CacheTime(Enum):
    """
    Enumeration of available cache times.

    - DONT_CACHE - don't cache.
    - KEEP - cache without expiry
    - others are the number of seconds in the given time period
    """

    DONT_CACHE = 0
    KEEP = 1
    FIVE_MINUTES = 300
    THIRTY_MINUTES = 1800
    ONE_DAY = 86400
    ONE_WEEK = 604800
    ONE_MONTH = 2629800
