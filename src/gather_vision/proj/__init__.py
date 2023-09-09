import configparser
import os
import pathlib


class DjangoCustomSettings:
    _prefix: str | None = None
    _config_parser: configparser.ConfigParser
    _successful_paths = []

    def __init__(self, prefix: str | None = None) -> None:
        self._prefix = prefix

    def load_env(self, name: str) -> None:
        name = self._prefixed_key(name)
        value = os.environ.get(name)
        if not value:
            msg = f"Env var '{name}' is not set."
            raise ValueError(msg)

        self.load_file(pathlib.Path(value))

    def load_file(self, path: pathlib.Path) -> None:
        self._config_parser = configparser.ConfigParser()
        self._successful_paths = self._config_parser.read(path)

    def get_str(self, key: str, default: str | None = None) -> str:
        value = self._config_parser.get(self._section, key, fallback=default)
        return value

    def get_bool(self, key: str, default: bool | None = None) -> bool:
        value = self._config_parser.getboolean(self._section, key, fallback=default)
        return value

    def get_int(self, key: str, default: bool | None = None) -> bool:
        value = self._config_parser.getint(self._section, key, fallback=default)
        return value

    def get_float(self, key: str, default: bool | None = None) -> bool:
        value = self._config_parser.getfloat(self._section, key, fallback=default)
        return value

    def get_list(
        self,
        key: str,
        sep: str = ",",
        default: list | None = None,
    ) -> list:
        value = self._config_parser.get(self._section, key, fallback=default or "")
        items = value.split(sep)
        return items

    def get_dict(
        self,
        key: str,
        sep_items: str = ";",
        sep_key_pair: str = "=",
        default: dict | None = None,
    ) -> dict:
        value = self._config_parser.get(self._section, key, fallback=default or "")
        items = value.split(sep_items)
        key_pairs = [i.split(sep_key_pair, maxsplit=1) for i in items]
        key_pairs = [i for i in key_pairs if i and i[0] and len(i) == 2]

        keys_all = sorted([i[0] for i in key_pairs if i and i[0]])
        keys_dup = sorted([i for i in keys_all if keys_all.count(i) > 1])
        if keys_dup:
            msg = f"Invalid value for key '{key}'. Found duplicate item keys '{sorted(keys_dup)}'."
            raise ValueError(
                msg,
            )

        result = {i[0]: i[1] for i in key_pairs}
        return result

    def get_path(
        self,
        key: str,
        default: pathlib.Path | None = None,
    ) -> pathlib.Path | None:
        value = self._config_parser.get(self._section, key, fallback=default or "")
        if value:
            return pathlib.Path(value)
        return None

    def _prefixed_key(self, value: str) -> str:
        if self._prefix:
            return f"{self._prefix}_{value}"
        return value

    @property
    def _section(self) -> str:
        if self._prefix:
            return self._prefix
        return self._config_parser.default_section
