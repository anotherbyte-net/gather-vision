from dataclasses import dataclass


@dataclass(frozen=True)
class PlaylistConf:

    source_code: str
    source_collection: str

    target_code: str
    target_playlist_id: str
    target_title: str
