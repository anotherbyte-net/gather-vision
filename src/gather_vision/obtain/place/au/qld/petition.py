import dataclasses
import typing

from gather_vision.obtain.core import data


@dataclasses.dataclass(frozen=True)
class QueenslandGovernmentPetitionItem(data.GatherDataItem):
    pass


class QueenslandGovernmentPetitionsWebData(data.WebData):
    base_url = "https://www.parliament.qld.gov.au/Work-of-the-Assembly/Petitions"
    current_url = f"{base_url}/Current-EPetitions"

    # div.current-petitions

    # item: .petitions-listing__details-wrapper
    # closing date: .petitions-listing__subtext
    # signature count: .petitions-listing__signatures-highlight
    # title: .petitions-listing__details-row a (text)
    # url: .petitions-listing__details-row a (href)
    # id: .petitions-listing__details-row span strong (not including 'a')

    closed_url = f"{base_url}/Closed-EPetitions"

    # No.
    # Subject	 (+url and id)
    # Closed
    # Number of Signatures	 (int)
    # Tabled	 (date)
    # Referred to Minister(s)	 (name)
    # Date Referred	(date)
    # Response Due	(date)
    # Response Tabled - (date and url)
    # e6a02297-f541-4a29-85c5-0ba6aff24b8d

    paper_url = f"{base_url}/Tabled-Paper-Petitions"

    # No.
    # Subject
    # Number of Signatures
    # Tabled
    # Referred to Minister(s)
    # Date Referred
    # Response Due
    # Response Tabled

    item_url = f"{base_url}/Petition-Details?id="

    # principal petitioner: .petition-details__petitioner-details-wrapper
    # signature count: .petition-details__signatures-highlight
    # addressed to: .petition-details__content--heading
    # body: .petition-details__content--body

    # sponsoring member: .petition-details__prop
    # posting date: .petition-details__prop
    # (online) closing date: .petition-details__prop
    # (paper) tabled date: .petition-details__prop
    # (online) sign url:

    resp_url = "https://apps.parliament.qld.gov.au/E-Petitions/Home/DownloadResponse"

    @property
    def name(self) -> str:
        return "au-qld-petitions"

    @property
    def tags(self) -> dict[str, str]:
        return {
            "country": "Australia",
            "region": "Queensland",
            "data_source_location": "web",
            "data_source_category": "petition",
        }

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.current_url]

    def web_resources(
        self, web_data: data.WebDataAvailable
    ) -> typing.Iterable[typing.Union[str, data.GatherDataItem]]:
        yield None
