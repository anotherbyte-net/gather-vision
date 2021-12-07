import base64
import secrets
import webbrowser
from urllib.parse import urlencode

from zoneinfo import ZoneInfo
from requests import Response, codes

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger


class SpotifyClient:
    """Spotify Music client."""

    def __init__(self, logger: Logger, http_client: HttpClient, time_zone: ZoneInfo):
        self._logger = logger
        self._http_client = http_client
        self._time_zone = time_zone

    def playlist_tracks_get(
        self,
        access_token: str,
        playlist_id: str,
        limit: int,
        offset: int = 0,
        market: str = "AU",
    ) -> tuple[int, dict]:
        """Get the tracks in a playlist."""
        if not access_token or not playlist_id:
            raise ValueError("Must provide access token and playlist id.")
        if not limit:
            limit = 100
        if not offset:
            offset = 0
        if not market:
            market = "AU"

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        params = {
            "fields": "items(track(name,id,artists(name)))",
            "market": market,
            "limit": limit,
            "offset": offset,
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        r = self._http_client.get(url, params=params, headers=headers)
        self._check_status(r)
        return r.status_code, r.json()

    def playlist_tracks_set(
        self,
        access_token: str,
        playlist_id: str,
        song_ids: list[str],
    ):
        """Replace songs in a playlist."""
        if not access_token or not playlist_id or not song_ids:
            raise ValueError("Must provide access token and playlist id and song ids.")

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        params = {"uris": [f"spotify:track:{song_id}" for song_id in song_ids]}
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        r = self._http_client.put(url, json=params, headers=headers)
        self._check_status(r)
        return r.status_code, r.json()

    def playlist_details_set(
        self,
        access_token: str,
        playlist_id: str,
        title: str,
        description: str,
        is_public: bool,
    ):
        """Set playlist details."""
        if not access_token or not playlist_id:
            raise ValueError("Must provide access token and playlist id.")
        if not title or not description or is_public is None:
            raise ValueError("Must provide title and description and is public.")

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        data = {
            "name": title,
            "description": description,
            "public": True if is_public else False,
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        r = self._http_client.put(url, json=data, headers=headers)
        self._check_status(r)
        return r.status_code, None

    def track_query_get(
        self, access_token: str, query: str, limit: int = 5
    ) -> tuple[int, dict]:
        """Find matching tracks."""
        if not access_token or not query:
            raise ValueError("Must provide access token and query.")
        if not limit:
            limit = 5

        url = "https://api.spotify.com/v1/search"
        params = {
            "q": query,
            "limit": limit,
            "offset": 0,
            "type": "track",
            "market": "AU",
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        r = self._http_client.get(url, params=params, headers=headers)
        self._check_status(r)
        return r.status_code, r.json()

    def login_authorise(
        self, client_id: str, redirect_uri: str, request_state: str
    ) -> None:
        """Get the url to obtain the Authorization Code."""
        if not client_id or not redirect_uri or not request_state:
            raise ValueError(
                "Must provide client id and redirect uri and request state."
            )

        qs = urlencode(
            {
                "client_id": client_id,
                "response_type": "code",
                "redirect_uri": redirect_uri,
                "scope": "playlist-modify-public",
                "state": request_state,
            }
        )
        url = "https://accounts.spotify.com/authorize?{qs}".format(qs=qs)
        webbrowser.open(url, new=2)

    def login_token_first(
        self, client_id: str, client_secret: str, auth_code: str, redirect_uri: str
    ) -> tuple[str, str, int]:
        """Get the initial access token and refresh token."""
        if not client_id or not client_secret or not auth_code or not redirect_uri:
            raise ValueError(
                "Must provide client id and client secret "
                "and auth code and redirect uri."
            )
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        r = self._http_client.post("https://accounts.spotify.com/api/token", data=data)
        self._check_status(r)
        response = r.json()

        access_token = response.get("access_token")
        expires_in = response.get("expires_in")
        refresh_token = response.get("refresh_token")
        return access_token, refresh_token, expires_in

    def login_token_next(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
    ) -> str:
        """Get the next login token."""
        if not client_id or not client_secret or not refresh_token:
            raise ValueError(
                "Must provide client id and client secret and refresh token."
            )

        self._logger.info("Get next Spotify login.")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        auth_basic_token = self._login_client_auth(client_id, client_secret)
        headers = {
            "Authorization": f"Basic {auth_basic_token}",
        }

        url = "https://accounts.spotify.com/api/token"
        r = self._http_client.post(url, data=data, headers=headers)
        self._check_status(r)
        response = r.json()
        access_token = response.get("access_token")

        if not access_token:
            raise ValueError("Invalid access token.")

        return access_token

    def login_init(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> tuple[str, str, int]:
        """Run the initial authorisation flow."""
        if not client_id or not client_secret or not redirect_uri:
            raise ValueError(
                "Must provide client id and client secret and redirect uri."
            )

        # docs:
        # https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow
        self._logger.info("Initialise Spotify login.")

        if not client_id or not client_secret:
            raise ValueError("Must provide client_id and client_secret.")

        request_state = secrets.token_hex(10)

        self.login_authorise(client_id, redirect_uri, request_state)
        auth_code = input("Enter the 'code' from the authorisation url:")

        access_token, refresh_token, expires_in = self.login_token_first(
            client_id, client_secret, auth_code, redirect_uri
        )

        self._logger.warning(f"Spotify access_token: {access_token}")
        self._logger.warning(f"Spotify refresh_token: {refresh_token}")
        self._logger.warning(f"Spotify expires_in: {expires_in / 60.0 / 60.0} hours")

        if not access_token or not refresh_token:
            raise ValueError("Invalid access token or refresh token.")

        return access_token, refresh_token, expires_in

    def _login_client_auth(self, client_id: str, client_secret: str):
        """Encode the client auth token."""
        basic = f"{client_id}:{client_secret}"
        basic_b64 = base64.b64encode(basic.encode())
        return basic_b64.decode()

    def _check_status(self, r: Response):
        """Check the http response code."""
        expected_codes = [codes.ok, codes.created]
        if r.status_code not in expected_codes:
            raise ValueError(f"Error in response - {r.status_code}:{r.text}.")
