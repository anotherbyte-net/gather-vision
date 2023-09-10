import dataclasses
import typing

from gather_vision.obtain.core import data


@dataclasses.dataclass
class QueenslandGovernmentPetitionItem(data.GatherDataItem):
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

    @property
    def tags(self) -> dict[str, str]:
        return {
            "country": "Australia",
            "region": "Queensland",
            "data_source_location": "web",
            "data_source_category": "petition",
        }

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.list_url]

    def web_resources(
        self, web_data: data.WebDataAvailable
    ) -> typing.Iterable[typing.Union[str, data.GatherDataItem]]:
        pass
