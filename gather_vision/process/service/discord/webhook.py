from dataclasses import field
from typing import Optional

from gather_vision.process.service.discord.embed import Embed


class Webhook:
    """A discord webhook. Supports content and embeds."""

    # https://discord.com/developers/docs/resources/webhook#execute-webhook-jsonform-params

    webhook_id: str
    webhook_token: str

    content: Optional[str] = None
    embeds: list[Embed] = field(default_factory=list)

    tts: bool = False

    username: Optional[str] = None
    avatar_url: Optional[str] = None

    wait: bool = False
    thread_id: Optional[str] = None

    def to_json(self):
        if self.content and self.embeds:
            raise ValueError("Cannot provide both content and embeds.")

        result = {
            "tts": "true" if self.tts else "false",
        }

        if self.content:
            result["content"] = self.content
        if self.embeds:
            result["embeds"] = [i.to_json() for i in self.embeds]
        if self.username:
            result["username"] = self.username
        if self.avatar_url:
            result["avatar_url"] = self.avatar_url

        return result
