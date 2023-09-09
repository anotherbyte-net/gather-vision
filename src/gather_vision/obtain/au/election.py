import dataclasses
import typing

from gather_vision.plugin import data


@dataclasses.dataclass
class AustraliaElectionItem:
    pass


class AustraliaElection(data.WebData):
    # https://results.aec.gov.au/
    # name: div#fedArchive li a[text]
    # url: div#fedArchive li a[href]

    # could use known paths to files
    # could also gather links from the page using the link titles or file paths
    # https://results.aec.gov.au/13745/Website/Downloads/HouseVotesCountedByDivisionDownload-13745.csv

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.list_url]

    def parse_response(
        self, data: data.WebDataAvailable
    ) -> typing.Generator[typing.Union[str, data.IsDataclass], typing.Any, typing.Any]:
        pass
