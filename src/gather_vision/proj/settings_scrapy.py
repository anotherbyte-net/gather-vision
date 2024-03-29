"""
The Scrapy settings for the project.
"""
import pathlib
from importlib.resources import path, files

from importlib_resources import as_file

from gather_vision.proj import DjangoCustomSettings


def make_scrapy_path(path: pathlib.Path) -> str:
    return str(path).replace("\\", "/")


with as_file(files("gather_vision.proj").joinpath("settings_scrapy.py")) as p:
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = p.parent.parent.parent.parent

# local dirs
LOCAL_DIR = BASE_DIR / ".local"

FEEDS_FILE_PATH = LOCAL_DIR / "feeds" / "feed_%(name)s_%(time)s.jsonl.gz"
HTTP_CACHE_DIR_PATH = LOCAL_DIR / "http_cache"
FILES_DIR_PATH = LOCAL_DIR / "files"

env = DjangoCustomSettings(prefix="GATHER_VISION_SCRAPY")
env.load_file(LOCAL_DIR / "gather_vision_scrapy.ini")
env.load_env(name="ENV_PATH")


USER_AGENT = env.get_str(
    "USER_AGENT",
    "gather-vision (+https://github.com/anotherbyte-net/gather-vision)",
)

# http cache
HTTPCACHE_ENABLED = env.get_bool(
    "HTTPCACHE_ENABLED",
    True,
)
HTTPCACHE_DIR = make_scrapy_path(
    env.get_path(
        "HTTPCACHE_DIR",
        HTTP_CACHE_DIR_PATH,
    ),
)
HTTPCACHE_POLICY = env.get_str(
    "HTTPCACHE_POLICY",
    "scrapy.extensions.httpcache.DummyPolicy",
    # "scrapy.extensions.httpcache.RFC2616Policy",
)
HTTPCACHE_STORAGE = env.get_str(
    "HTTPCACHE_STORAGE",
    "scrapy.extensions.httpcache.FilesystemCacheStorage",
)
EXTENSIONS = env.get_dict(
    "EXTENSIONS",
    default={
        "scrapy.extensions.telnet.TelnetConsole": None,
    },
)

# feed
FEEDS = env.get_dict(
    "FEEDS",
    default={
        f"file:///{make_scrapy_path(FEEDS_FILE_PATH)}": {
            "format": "jsonlines",
            "postprocessing": ["scrapy.extensions.postprocessing.GzipPlugin"],
            "gzip_compresslevel": 5,
        }
    },
)

# logs
LOG_ENABLED = env.get_bool("LOG_ENABLED", True)
LOG_FILE = env.get_path("LOG_FILE", None)
LOG_STDOUT = env.get_bool("LOG_STDOUT", False)
LOG_LEVEL = env.get_str("LOG_LEVEL", "WARNING")
LOG_SHORT_NAMES = env.get_bool("LOG_SHORT_NAMES", False)
LOG_FORMAT = env.get_str(
    "LOG_FORMAT", "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
LOG_DATEFORMAT = env.get_str("LOG_DATEFORMAT", "%Y-%m-%d %H:%M:%S")

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
        "scrapy.pipelines.files.FilesPipeline": 100,
        "gather_vision.obtain.core.data.GatherVisionStoreDjangoItemPipeline": 300,
    },
)

FILES_STORE = make_scrapy_path(env.get_path("FILES_STORE", FILES_DIR_PATH))
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
