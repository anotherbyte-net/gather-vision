from typing import Optional


class EmbedField:
    """A Discord embed field."""

    # https://discord.com/developers/docs/resources/channel#embed-object-embed-field-structure
    name: str
    value: str
    inline: Optional[bool] = None

    def to_json(self):
        result = {"name": self.name, "value": self.value}
        if self.inline is not None:
            result["inline"] = "true" if self.inline else "false"
        return result
