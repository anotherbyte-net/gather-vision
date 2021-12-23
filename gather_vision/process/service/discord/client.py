from typing import Optional

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.service.discord.webhook import Webhook


class Client:
    """Interface to the Discord API."""

    def __init__(
        self,
        logger: Logger,
        http_client: HttpClient,
        bot_name: str,
        bot_url: str,
        bot_version: str,
        base_url: Optional[str] = None,
    ):
        self._logger = logger
        self._http_client = http_client
        self._bot_name = bot_name
        self._bot_url = bot_url
        self._bot_version = bot_version

        # https://discord.com/developers/docs/reference#http-api
        self._base_url = base_url or f"https://discord.com/api/v9"

    def execute_webhook(self, info: Webhook):
        """Execute a discord webhook."""
        # https://discord.com/developers/docs/resources/webhook#execute-webhook

        params = {"wait": "true" if info.wait else "false"}

        if info.thread_id:
            params["thread_id"] = info.thread_id

        json_data = info.to_json()
        url = self._base_url + f"/webhooks/{info.webhook_id}/{info.webhook_token}"
        self._http_client.post(
            url,
            params=params,
            json=json_data,
            headers={
                "user-agent": f"{self._bot_name} ({self._bot_url},{self._bot_version})"
            },
        )
