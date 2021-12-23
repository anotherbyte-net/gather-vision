from pathlib import Path
from typing import Optional, Iterable

from zoneinfo import ZoneInfo
from ytmusicapi import YTMusic

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.item.track import Track


class YoutubeMusicClient:
    """YouTube Music client."""

    def __init__(self, logger: Logger, http_client: HttpClient, time_zone: ZoneInfo):
        self._logger = logger
        self._http_client = http_client
        self._time_zone = time_zone

        self._client: Optional[YTMusic] = None

    def playlist_tracks_get(
        self, playlist_id: str, limit: Optional[int] = None
    ) -> dict:
        """Get the tracks in a playlist."""
        if not playlist_id:
            raise ValueError("Must provide playlist id.")

        if limit is None:
            raw = self._client.get_playlist(playlist_id) or {}
        else:
            raw = self._client.get_playlist(playlist_id, limit) or {}
        return raw

    def playlist_tracks_set(
        self, playlist_id: str, new_tracks: Iterable[Track], old_tracks: Iterable[Track]
    ) -> bool:
        """Replace songs in a playlist."""
        if not playlist_id or (not new_tracks and not old_tracks):
            raise ValueError(
                "Must provide playlist id and "
                "at least one of new tracks and old tracks."
            )

        if old_tracks:
            result = self._client.remove_playlist_items(
                playlist_id,
                [
                    {
                        "videoId": t.track_id,
                        "setVideoId": t.raw.get("setVideoId"),
                    }
                    for t in old_tracks
                ],
            )

            if result != "STATUS_SUCCEEDED":
                return False

        result = self._client.add_playlist_items(
            playlist_id,
            [t.track_id for t in new_tracks],
            source_playlist=None,
            duplicates=False,
        )
        if "status" not in result or result.get("status") != "STATUS_SUCCEEDED":
            return False

        return True

    def playlist_details_set(
        self,
        playlist_id: str,
        title: str = None,
        description: str = None,
        is_public: bool = None,
    ):
        """Set playlist details."""
        if not playlist_id:
            raise ValueError("Must provide playlist id.")
        if not title or not description or is_public is None:
            raise ValueError("Must provide title and description and is public.")

        result = self._client.edit_playlist(
            playlistId=playlist_id,
            title=title,
            description=description,
            privacyStatus="PUBLIC" if is_public else "PRIVATE",
        )
        return result == "STATUS_SUCCEEDED"

    def track_query_get(self, query: str, limit: int = 5) -> Iterable[dict]:
        """Find matching tracks."""
        result = self._client.search(
            query=query, filter="songs", limit=limit, ignore_spelling=False
        )
        return result

    def login_token_next(self, credentials: str):
        """Get the next login token."""
        self._logger.info("Get next YouTube Music login.")
        self._client = YTMusic(
            auth=credentials, requests_session=self._http_client.session
        )

    def login_init(self):
        """Prompt for the initial YouTube headers."""
        self._logger.info("Initialise YouTube Music login.")

        msg = "Paste path to the request header file from https://music.youtube.com:"
        file_path = input(msg)
        if not file_path:
            raise ValueError("Provide the file path.")

        path = Path(file_path)
        if not path.is_file():
            raise ValueError(f"Invalid file path '{path}'.")

        request_headers = path.read_text()
        creds_json = YTMusic.setup(filepath=None, headers_raw=request_headers)

        self._logger.warning(f"YouTubeMusic credentials: {creds_json}")

        return creds_json
