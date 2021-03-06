from abc import ABC
from datetime import datetime
from typing import Optional, Iterable

from gather_vision.process import item as app_items
from gather_vision import models as app_models


class PlaylistSource(ABC):
    """A service that provides playlists."""

    @property
    def collections(self) -> list:
        """
        The internal codes for the playlists available from this service.
        """
        raise NotImplementedError()

    def get_playlist(
        self, identifier: str, name: str, title: str
    ) -> app_items.Playlist:
        """Get a playlist."""
        raise NotImplementedError()

    def get_playlist_tracks(
        self,
        identifier: str,
        name: str,
        title: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> app_items.Playlist:
        """Get a playlist and tracks."""
        raise NotImplementedError()

    def get_model_track(
        self,
        info: app_models.InformationSource,
        track: app_items.Track,
    ) -> app_models.PlaylistTrack:
        """Convert from a track from this source to the model used to store a track."""
        raise NotImplementedError()


class PlaylistTarget(ABC):
    """A service that can store playlists."""

    def set_playlist_tracks(
        self,
        identifier: str,
        new_tracks: Iterable[app_items.Track],
        old_tracks: Iterable[app_items.Track],
    ) -> bool:
        """Set the tracks for a playlist."""
        raise NotImplementedError()

    def set_playlist_details(
        self,
        collection_name: str,
        playlist_id: str,
        title: str = None,
        description: str = None,
        is_public: bool = None,
    ) -> bool:
        """Set playlist details."""
        raise NotImplementedError()

    def search_tracks(
        self,
        playlist_name: str,
        track: str,
        artists: list[str],
        limit: int = 5,
    ) -> Iterable[app_items.Track]:
        """Search the tracks available from a service."""
        raise NotImplementedError()


class AuthRequiredService(ABC):
    """A service that requires authentication."""

    def login_init(self, *args, **kwargs) -> None:
        """Get the initial set of login details."""
        raise NotImplementedError()

    def login_next(self, *args, **kwargs) -> None:
        """Get the next set of login details."""
        raise NotImplementedError()


class PlaylistDetails(ABC):
    """Provided basic information about a playlist service."""

    @property
    def code(self) -> str:
        """The internal code for the service."""
        raise NotImplementedError()

    @property
    def title(self) -> str:
        """The displayed title for the service."""
        raise NotImplementedError()
