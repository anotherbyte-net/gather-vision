"""
The Scrapy settings for the project.
"""

from importlib.resources import path
from gather_vision.proj import DjangoCustomSettings

with path("gather_vision.proj", "settings_scrapy.py") as p:
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = p.parent.parent.parent.parent

LOCAL_DIR = BASE_DIR / ".local"

FEEDS_PICKLE_FILE = LOCAL_DIR / "feeds" / "feed_%(name)s_%(time)s.pickle"

env = DjangoCustomSettings(prefix="GATHER_VISION_SCRAPY")
env.load_file(LOCAL_DIR / ".env_scrapy")
env.load_env(name="ENV_PATH")


USER_AGENT = env.get_str(
    "USER_AGENT",
    "gather-vision (+https://github.com/anotherbyte-net/gather-vision)",
)

# http cache
HTTPCACHE_ENABLED = env.get_bool("HTTPCACHE_ENABLED", True)
HTTPCACHE_DIR = env.get_path("HTTPCACHE_DIR", LOCAL_DIR / "http_cache")
HTTPCACHE_POLICY = env.get_str(
    "HTTPCACHE_POLICY", "scrapy.extensions.httpcache.DummyPolicy"
)
HTTPCACHE_STORAGE = env.get_str(
    "HTTPCACHE_STORAGE",
    "scrapy.extensions.httpcache.FilesystemCacheStorage",
)
EXTENSIONS = env.get_dict(
    "EXTENSIONS", default={"scrapy.extensions.telnet.TelnetConsole": None}
)

# feed
FEED_EXPORTERS = env.get_dict(
    "FEED_EXPORTERS",
    default={
        "pickle_raw": "gather_vision.app.AppPickleItemExporter",
    },
)
FEEDS = env.get_dict(
    "FEEDS",
    default={
        f"file:///{FEEDS_PICKLE_FILE}": {
            "format": "pickle_raw",
        }
    },
)


# logs
LOG_ENABLED = env.get_bool("LOG_ENABLED", True)
LOG_FILE = env.get_path("LOG_FILE", None)
LOG_STDOUT = env.get_bool("LOG_STDOUT", False)
LOG_LEVEL = env.get_str("LOG_LEVEL", "ERROR")

# throttling requests
DOWNLOAD_DELAY = env.get_int("DOWNLOAD_DELAY", 3)
AUTOTHROTTLE_ENABLED = env.get_bool("AUTOTHROTTLE_ENABLED", True)
AUTOTHROTTLE_START_DELAY = env.get_int("AUTOTHROTTLE_START_DELAY", 3)
AUTOTHROTTLE_MAX_DELAY = env.get_int("AUTOTHROTTLE_MAX_DELAY", 60)
AUTOTHROTTLE_TARGET_CONCURRENCY = env.get_float(
    "AUTOTHROTTLE_TARGET_CONCURRENCY",
    1.0,
)

# pipelines
ITEM_PIPELINES = env.get_dict(
    "ITEM_PIPELINES",
    default={
        "scrapy.pipelines.files.FilesPipeline": 1,
    },
)

FILES_STORE = env.get_path("FILES_STORE", LOCAL_DIR / "files")
MEDIA_ALLOW_REDIRECTS = env.get_bool("MEDIA_ALLOW_REDIRECTS", True)

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = env.get_str(
    "REQUEST_FINGERPRINTER_IMPLEMENTATION",
    "2.7",
)
TWISTED_REACTOR = env.get_str(
    "TWISTED_REACTOR",
    "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
)
FEED_EXPORT_ENCODING = env.get_str(
    "FEED_EXPORT_ENCODING",
    "utf-8",
)
