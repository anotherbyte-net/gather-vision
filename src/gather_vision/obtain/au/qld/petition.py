import dataclasses
import typing

from gather_vision.plugin import data


@dataclasses.dataclass
class QueenslandGovernmentPetitionItem:
    pass


class QueenslandGovernmentPetitions(data.WebData):
    base_url = "https://www.parliament.qld.gov.au/Work-of-the-Assembly/Petitions"
    list_url = f"{base_url}/Current-EPetitions"

    # div.current-petitions

    # item: .petitions-listing__details-wrapper
    # closing date: .petitions-listing__subtext
    # signature count: .petitions-listing__signatures-highlight
    # title: .petitions-listing__details-row a (text)
    # url: .petitions-listing__details-row a (href)
    # id: .petitions-listing__details-row span strong (not including 'a')

    item_url = f"{base_url}/Petition-Details?id=${{item_id}}"

    # principal petitioner: .petition-details__petitioner-details-wrapper
    # signature count: .petition-details__signatures-highlight
    # addressed to: .petition-details__content--heading
    # body: .petition-details__content--body

    # sponsoring member: .petition-details__prop
    # posting date: .petition-details__prop
    # closing date: .petition-details__prop

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.list_url]

    def parse_response(
        self, data: data.WebDataAvailable
    ) -> typing.Generator[typing.Union[str, data.IsDataclass], typing.Any, typing.Any]:
        pass
