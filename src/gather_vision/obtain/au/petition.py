import dataclasses
import typing

from gather_vision.plugin import data


@dataclasses.dataclass
class AustralianGovernmentPetitionItem:
    pass


class AustralianGovernmentPetitions(data.WebData):
    list_url = "https://www.aph.gov.au/e-petitions"
    item_url = f"{list_url}/petition/${{item_id}}"

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.list_url]

    def parse_response(
        self, data: data.WebDataAvailable
    ) -> typing.Generator[typing.Union[str, data.IsDataclass], typing.Any, typing.Any]:
        pass
