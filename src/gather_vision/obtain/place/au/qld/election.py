import io
import logging
import typing
from zipfile import ZipFile

from gather_vision.obtain.core import data
from gather_vision.obtain.core.data import (
    WebDataAvailable,
    GatherDataRequest,
    GatherDataItem,
)
from gather_vision.obtain.core.utils import xml_to_data

logger = logging.getLogger(__name__)


class QueenslandGovernmentElectionsWebData(data.WebData):
    # 'All You Need To Know' html tables index page
    list_ecq_results_index_url = "https://results.ecq.qld.gov.au/elections/index.html"
    # Past Elections, links to dynamic pages built from json files
    list_elections_resultsdata_url = (
        "https://resultsdata.elections.qld.gov.au/elections.json"
    )
    # Current and recent results, links to a  mixture of page types
    list_ecq_results_url = "https://www.ecq.qld.gov.au/elections/election-results"

    # known ECQ domains
    base_ecq_results_url = "https://results.ecq.qld.gov.au/"
    base_ecq_results1_url = "https://results1.ecq.qld.gov.au/"
    base_ecq_www_url = "https://www.ecq.qld.gov.au/"
    base_elections_results1_url = "https://results1.elections.qld.gov.au/"
    base_elections_resultsdata_url = "https://resultsdata.elections.qld.gov.au/"
    base_elections_results_url = "https://results.elections.qld.gov.au/"

    @property
    def name(self) -> str:
        return "au-qld-elections"

    def initial_urls(self) -> typing.Iterable[str]:
        return [
            self.list_ecq_results_index_url,
            self.list_elections_resultsdata_url,
            self.list_ecq_results_url,
        ]

    def web_resources(
        self, web_data: WebDataAvailable
    ) -> typing.Iterable[typing.Union[GatherDataRequest, GatherDataItem]]:
        url = web_data.response_url
        if url == self.list_ecq_results_index_url:
            yield from self._parse_ecq_result_index(web_data)
        elif url == self.list_elections_resultsdata_url:
            yield from self._parse_elections_resultsdata(web_data)
        elif url == self.list_ecq_results_url:
            yield from self._parse_ecq_result(web_data)
        else:
            yield from self._parse_data(web_data)

    def _parse_ecq_result_index(
        self, web_data: WebDataAvailable
    ) -> typing.Iterable[typing.Union[GatherDataRequest, GatherDataItem]]:
        for section in web_data.selector.css('td[colspan="4"]'):
            section_title = section.css("::text").get()
            for following_sibling in section.xpath("../following-sibling::tr"):
                tds = following_sibling.css("td")
                first_td = tds[0]
                if first_td.attrib.get("colspan") == "4":
                    break
                if first_td.attrib.get("colspan") == "3":
                    continue
                entry_title = tds[1].css("::text").get()

                summary_url = tds[2].css("a").attrib.get("href")
                if summary_url:
                    yield data.GatherDataRequest(
                        url=self._make_abs_url(self.base_ecq_results_url, summary_url),
                        data={
                            "section_title": section_title,
                            "entry_title": entry_title,
                        },
                    )

                index_url = tds[3].css("a").attrib.get("href")
                if index_url:
                    yield data.GatherDataRequest(
                        url=self._make_abs_url(self.base_ecq_results_url, index_url),
                        data={
                            "section_title": section_title,
                            "entry_title": entry_title,
                        },
                    )

    def _parse_elections_resultsdata(
        self, web_data: WebDataAvailable
    ) -> typing.Iterable[typing.Union[GatherDataRequest, GatherDataItem]]:
        for election in web_data.body_data.get("elections"):
            el_stub = election.get("stub")
            el_data = {
                "el_id": election.get("id"),
                "entry_title": election.get("electionName"),
                "el_type": election.get("electionType"),
                "el_day": election.get("electionDay"),
                "el_date1": election.get("electionDate1"),
                "el_date2": election.get("electionDate2"),
                "el_date3": election.get("electionDate3"),
                "el_stub": el_stub,
                "el_event_details": election.get("eventDetails"),
                "el_enrolment": election.get("enrolment"),
                "el_visible": election.get("visible"),
                "el_indicative_count": election.get("indicativeCount"),
                "el_indicative_details_booth": election.get("indicativeDetailsBooth"),
                "el_preference_details_booth": election.get("preferenceDetailsBooth"),
                "el_default_count_round": election.get("defaultCountround"),
                "el_current": election.get("current"),
            }
            urls = [
                election.get("archiveXML"),
                election.get("electorates"),
                election.get("boundaryVenues"),
                f"{el_stub}-banners.json",
                f"{el_stub}-declared_candidates.json",
                f"{el_stub}-status.json",
            ]
            for url in urls:
                url = self._make_abs_url(self.base_elections_resultsdata_url, url)
                yield data.GatherDataRequest(url=url, data=el_data)

    def _parse_ecq_result(
        self, web_data: WebDataAvailable
    ) -> typing.Iterable[typing.Union[GatherDataRequest, GatherDataItem]]:
        for anchor in web_data.selector.css("div.content__main ul li a"):
            url = anchor.attrib.get("href")
            title = anchor.css("::text").get()
            if url:
                yield data.GatherDataRequest(url=url, data={"entry_title": title})

    def _parse_data(
        self, web_data: WebDataAvailable
    ) -> typing.Iterable[typing.Union[GatherDataRequest, GatherDataItem]]:
        url = web_data.response_url
        is_ecq_results1 = url.startswith(self.base_ecq_results1_url)
        is_elections_resultsdata = url.startswith(self.base_elections_resultsdata_url)
        is_elections_results1 = url.startswith(self.base_elections_results1_url)
        if url.endswith(".zip"):
            yield from self._parse_data_zip_xml(url, web_data)
        elif url.startswith(self.base_elections_results_url) and not url.endswith(
            ".json"
        ):
            yield from self._parse_data_html(url, web_data)
        elif is_elections_resultsdata and url.endswith("-status.json"):
            yield from self._parse_data_status(url, web_data)
        elif is_elections_resultsdata and url.endswith("-banners.json"):
            yield from self._parse_data_banner(url, web_data)
        elif is_elections_resultsdata and url.endswith("-declared_candidates.json"):
            yield from self._parse_data_candidates(url, web_data)
        elif is_elections_resultsdata and url.endswith("-boundary_venues.json"):
            yield from self._parse_data_boundary_venues(url, web_data)
        elif is_elections_resultsdata and url.endswith("-electorates.json"):
            yield from self._parse_data_electorates(url, web_data)
        elif url.startswith(self.base_ecq_results_url) and url.endswith(".html"):
            yield from self._parse_ecq_results_summary(url, web_data)
        elif is_elections_results1:
            yield from self._parse_elections_results1_html(url, web_data)
        elif is_ecq_results1:
            yield from self._parse_ecq_results1(url, web_data)
        elif url.startswith(self.base_ecq_www_url):
            yield from self._parse_ecq_www(url, web_data)
        else:
            raise ValueError(url, web_data)

    def _parse_zip_xml(self, web_data: WebDataAvailable):
        url = web_data.response_url
        with io.BytesIO(web_data.body_raw) as zip_data:
            with ZipFile(zip_data, "r") as zip_reader:
                if logger.isEnabledFor(logging.DEBUG):
                    zip_test = zip_reader.testzip()
                    if zip_test is not None:
                        raise ValueError(f"Bad zip file '{url}': {zip_test}")

                file_list = zip_reader.infolist()
                for file_info in file_list:
                    if not file_info.filename.endswith("xml"):
                        continue
                    file_data = zip_reader.read(file_info.filename).decode("utf-8")
                    return xml_to_data(file_data)

    def _parse_data_zip_xml(self, url: str, web_data: WebDataAvailable):
        xml_data = self._parse_zip_xml(web_data)
        yield None

    def _parse_data_html(self, url: str, web_data: WebDataAvailable):
        # TODO: parse 'https://results.elections.qld.gov.au/aurukun2020/01'
        yield None

    def _parse_data_status(self, url: str, web_data: WebDataAvailable):
        # TODO: parse 'https://resultsdata.elections.qld.gov.au/bundamba2020-status.json'
        yield None

    def _parse_data_banner(self, url: str, web_data: WebDataAvailable):
        # TODO: parse 'https://resultsdata.elections.qld.gov.au/bundamba2020-banner.json'
        yield None

    def _parse_ecq_results_summary(self, url: str, web_data: WebDataAvailable):
        # TODO: parse 'https://results.ecq.qld.gov.au/elections/state/REF2016/results/summary.html'
        yield None

    def _parse_data_candidates(self, url: str, web_data: WebDataAvailable):
        # TODO: parse 'https://resultsdata.elections.qld.gov.au/bundamba2020-declared_candidates.json'
        yield None

    def _parse_data_boundary_venues(self, url: str, web_data: WebDataAvailable):
        yield None

    def _parse_data_electorates(self, url: str, web_data: WebDataAvailable):
        yield None

    def _parse_elections_results1_html(self, url: str, web_data: WebDataAvailable):
        yield None

    def _parse_ecq_results1(self, url: str, web_data: WebDataAvailable):
        yield None

    def _parse_ecq_www(self, url: str, web_data: WebDataAvailable):
        yield None
