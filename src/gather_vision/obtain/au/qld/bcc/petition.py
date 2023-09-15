import dataclasses
import typing

from gather_vision.obtain.core import data


@dataclasses.dataclass
class BrisbaneCityCouncilPetitionItem(data.GatherDataItem):
    pass


class BrisbaneCityCouncilPetitionsWebData(data.WebData):
    @property
    def tags(self) -> dict[str, str]:
        return {
            "country": "Australia",
            "region": "Queensland",
            "district": "Brisbane City Council",
            "locality": "City of Brisbane",
            "data_source_location": "web",
            "data_source_category": "petition",
        }

    list_url = "https://www.epetitions.brisbane.qld.gov.au"
    # table.petitions
    # tbody.tr.th (headers)
    # tbody.tr.td (cells)

    item_url = f"{list_url}/petition/view/pid/${{item_id}}"

    # title: .page-title h1

    # content: #petition-page
    # table .petition-details (td.heading (headers),  td (no class) (values))

    # body: .petition-details

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.list_url]

    def web_resources(
        self, web_data: data.WebDataAvailable
    ) -> typing.Iterable[typing.Union[str, data.GatherDataItem]]:
        yield None

        # Options (pick one):
        # - return BrisbaneCityCouncilPetitionItem
        # - return a list of urls to get and parse
