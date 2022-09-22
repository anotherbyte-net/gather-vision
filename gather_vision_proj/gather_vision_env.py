from urllib.parse import urlparse, parse_qs

from environ import ImproperlyConfigured, FileAwareEnv

from gather_vision.process.item.playlist_conf import PlaylistConf


class GatherVisionEnv(FileAwareEnv):

    DEFAULT_EXTERNAL_HTTP_CACHE_ENV = "EXTERNAL_HTTP_CACHE_URL"

    # https://requests-cache.readthedocs.io/en/stable/user_guide/backends.html
    EXTERNAL_HTTP_CACHE_SCHEMES = {
        "sqlite": "requests_cache.backends.sqlite.SQLiteCache",
        "noop": None,
        "filesystem": "requests_cache.backends.filesystem.FileCache",
        "memory": "requests_cache.backends.base.BaseCache",
    }

    DEFAULT_PLAYLIST_SOURCES_TARGETS_ENV = "PLAYLIST_SOURCES_TARGETS"

    def external_http_cache_url(
        self,
        var=DEFAULT_EXTERNAL_HTTP_CACHE_ENV,
        default=FileAwareEnv.NOTSET,
        backend=None,
    ):
        """Returns a config dictionary, defaulting to EXTERNAL_HTTP_CACHE_URL.

        :rtype: dict
        """
        return self.external_http_cache_url_config(
            self.url(var, default=default), backend=backend
        )

    @classmethod
    def external_http_cache_url_config(cls, url, backend=None):
        """Pulled from DJ-Cache-URL, parse an arbitrary Cache URL.

        :param url:
        :param backend:
        :return:
        """
        if not isinstance(url, cls.URL_CLASS):
            if not url:
                return {}
            else:
                url = urlparse(url)

        if url.scheme not in cls.EXTERNAL_HTTP_CACHE_SCHEMES:
            raise ImproperlyConfigured("Invalid cache schema {}".format(url.scheme))

        location = url.netloc.split(",")
        if len(location) == 1:
            location = location[0]

        querystring = parse_qs(url.query) if url.query else {}
        backend_params = {}
        for key, values in querystring.items():
            if len(values) == 0:
                backend_params[key] = None
            elif len(values) == 1:
                backend_params[key] = values[0]
            else:
                backend_params[key] = values

        config = {
            "BACKEND": cls.EXTERNAL_HTTP_CACHE_SCHEMES[url.scheme],
            "LOCATION": location or url.path,
            "EXPIRES": backend_params.pop(
                "expires", backend_params.pop("EXPIRES", None)
            ),
            "BACKEND_PARAMS": backend_params,
        }

        return config

    def playlist_sources_targets(
        self,
        var=DEFAULT_PLAYLIST_SOURCES_TARGETS_ENV,
        default=None,
        backend=None,
    ) -> list[PlaylistConf]:

        items = self.json(var, default or [])
        result = []
        for item in items:
            result.append(
                PlaylistConf(
                    source_code=item.get("source", {}).get("code"),
                    source_collection=item.get("source", {}).get("collection"),
                    target_code=item.get("target", {}).get("code"),
                    target_playlist_id=item.get("target", {}).get("playlist_id"),
                    target_title=item.get("target", {}).get("title"),
                )
            )
        return result
