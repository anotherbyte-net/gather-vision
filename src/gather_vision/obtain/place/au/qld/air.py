import dataclasses
import typing

from gather_vision.obtain.core import data
from gather_vision.obtain.core.data import WebDataAvailable, GatherDataItem


@dataclasses.dataclass(frozen=True)
class QueenslandAirItem(data.GatherDataItem):
    pass


class QueenslandAirWebData(data.WebData):
    @property
    def name(self) -> str:
        return "au-qld-air"

    def web_resources(
        self, web_data: data.WebDataAvailable
    ) -> typing.Iterable[typing.Union[str, data.GatherDataItem]]:
        yield None

    @property
    def tags(self) -> dict[str, str]:
        return {}

    # qld air quality
    # https://aqicn.org/station/@131722
    # https://www.iqair.com/au/australia/queensland/toowoomba/south-street
    # https://apps.des.qld.gov.au/air-quality/stations/?station=too1
    # https://apps.des.qld.gov.au/air-quality/xml/feed.php

    # qld fire
    # advisories: https://www.data.qld.gov.au/dataset/queensland-parks-and-wildlife-service-fire-advisories/resource/6ac556e2-6778-479b-9fd5-6ad5ed2def99
    # planned burns: https://www.data.qld.gov.au/dataset/queensland-parks-and-wildlife-service-fire-advisories/resource/db74c713-a1cf-4109-be1f-b78130ec65d5

    def initial_urls(self) -> typing.Iterable[str]:
        return []

    def parse_response(
        self, data: data.WebDataAvailable
    ) -> typing.Generator[typing.Union[str, data.IsDataclass], typing.Any, typing.Any]:
        pass
