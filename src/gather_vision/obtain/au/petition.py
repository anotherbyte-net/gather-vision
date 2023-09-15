import dataclasses
import typing

from gather_vision.obtain.core import data
from gather_vision.obtain.core.data import WebDataAvailable, GatherDataItem


@dataclasses.dataclass
class AustralianGovernmentPetitionItem:
    pass


class AustralianGovernmentPetitionsWebData(data.WebData):
    def web_resources(
        self, web_data: data.WebDataAvailable
    ) -> typing.Iterable[typing.Union[str, data.GatherDataItem]]:
        yield None

    @property
    def tags(self) -> dict[str, str]:
        return {}

    list_url = "https://www.aph.gov.au/e-petitions"
    item_url = f"{list_url}/petition/${{item_id}}"

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.list_url]

    def parse_response(
        self, data: data.WebDataAvailable
    ) -> typing.Generator[typing.Union[str, data.IsDataclass], typing.Any, typing.Any]:
        pass
