from dataclasses import field
from datetime import datetime
from typing import Optional

from gather_vision.process.service.discord.embed_field import EmbedField


class Embed:
    """A Discord embed."""

    # https://discord.com/developers/docs/resources/channel#embed-object

    title: Optional[str] = None
    embed_type: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[datetime] = None
    color: Optional[int] = None

    footer_text: Optional[str] = None
    footer_icon_url: Optional[str] = None
    footer_proxy_icon_url: Optional[str] = None

    provider_name: Optional[str] = None
    provider_url: Optional[str] = None

    author_name: Optional[str] = None
    author_url: Optional[str] = None
    author_icon_url: Optional[str] = None
    author_proxy_icon_url: Optional[str] = None

    fields: list[EmbedField] = field(default_factory=list)

    def to_json(self):
        result = {}

        if self.title:
            result["title"] = self.title
        if self.embed_type:
            result["type"] = self.embed_type
        if self.description:
            result["description"] = self.description
        if self.url:
            result["url"] = self.url
        if self.timestamp:
            result["timestamp"] = self.timestamp.isoformat(timespec="seconds")
        if self.color:
            result["color"] = self.color

        if any([self.footer_text, self.footer_icon_url, self.footer_proxy_icon_url]):
            data = {}
            if self.footer_text:
                data["text"] = self.footer_text
            if self.footer_icon_url:
                data["icon_url"] = self.footer_icon_url
            if self.footer_proxy_icon_url:
                data["proxy_icon_url"] = self.footer_proxy_icon_url
            result["footer"] = data

        if any([self.provider_name, self.provider_url]):
            data = {}
            if self.provider_name:
                data["name"] = self.provider_name
            if self.provider_url:
                data["url"] = self.provider_url
            result["provider"] = data

        if any(
            [
                self.author_name,
                self.author_url,
                self.author_icon_url,
                self.author_proxy_icon_url,
            ]
        ):
            data = {}
            if self.author_name:
                data["name"] = self.author_name
            if self.author_url:
                data["url"] = self.author_url
            if self.author_icon_url:
                data["icon_url"] = self.author_icon_url
            if self.author_proxy_icon_url:
                data["proxy_icon_url"] = self.author_proxy_icon_url
            result["author"] = data

        if self.fields:
            result["fields"] = [i.to_json() for i in self.fields]

        return result
