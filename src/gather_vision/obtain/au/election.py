import dataclasses
import typing

from gather_vision.obtain.core import data


@dataclasses.dataclass
class AustraliaElectionItem:
    pass


class AustraliaElectionWebData(data.WebData):
    # https://results.aec.gov.au/
    # name: div#fedArchive li a[text]
    # url: div#fedArchive li a[href]

    # could use known paths to files
    # could also gather links from the page using the link titles or file paths
    # https://results.aec.gov.au/13745/Website/Downloads/HouseVotesCountedByDivisionDownload-13745.csv

    def initial_urls(self) -> typing.Iterable[str]:
        return []

    def parse_response(
        self, data: data.WebDataAvailable
    ) -> typing.Generator[typing.Union[str, data.IsDataclass], typing.Any, typing.Any]:
        pass

    def web_resources(
        self, web_data: data.WebDataAvailable
    ) -> typing.Iterable[typing.Union[str, data.GatherDataItem]]:
        yield None

    @property
    def tags(self) -> dict[str, str]:
        return {}
