import io
import typing
from zipfile import ZipFile

from gather_vision.obtain.core import data
from gather_vision.obtain.core.data import (
    WebDataAvailable,
    GatherDataRequest,
    GatherDataItem,
)
from gather_vision.obtain.core.utils import xml_to_data


class QueenslandGovernmentElectionsWebData(data.WebData):
    # 'All You Need To Know' html tables index page
    list_v1_url = "https://results.ecq.qld.gov.au/elections/index.html"
    # Past Elections, links to dynamic pages built from json files
    list_v2_url = "https://resultsdata.elections.qld.gov.au/elections.json"
    # Current and recent results, links to a  mixture of page types
    list_v3_url = "https://www.ecq.qld.gov.au/elections/election-results"

    list_base1_v1_url = "https://results.ecq.qld.gov.au/"
    # list_base2_v1_url = "https://results1.ecq.qld.gov.au/"
    list_base_v2_url = "https://resultsdata.elections.qld.gov.au/"
    list_base2_v2_url = "https://results.elections.qld.gov.au/"
    # list_base_v3_url = "https://www.ecq.qld.gov.au/"

    @property
    def name(self) -> str:
        return "au-qld-elections"

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.list_v1_url, self.list_v2_url, self.list_v3_url]

    def web_resources(
        self, web_data: WebDataAvailable
    ) -> typing.Iterable[typing.Union[GatherDataRequest, GatherDataItem]]:
        url = web_data.response_url
        if url == self.list_v1_url:
            yield from self._parse_list_v1(web_data)
        elif url == self.list_v2_url:
            yield from self._parse_list_v2(web_data)
        elif url == self.list_v3_url:
            yield from self._parse_list_v3(web_data)
        else:
            self._parse_data(web_data)

    def _parse_list_v1(
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
                        url=self._make_abs_url(self.list_base1_v1_url, summary_url),
                        data={
                            "section_title": section_title,
                            "entry_title": entry_title,
                        },
                    )

                index_url = tds[3].css("a").attrib.get("href")
                if index_url:
                    yield data.GatherDataRequest(
                        url=self._make_abs_url(self.list_base1_v1_url, index_url),
                        data={
                            "section_title": section_title,
                            "entry_title": entry_title,
                        },
                    )

    def _parse_list_v2(
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
                url = self._make_abs_url(self.list_base_v2_url, url)
                yield data.GatherDataRequest(url=url, data=el_data)

    def _parse_list_v3(
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
        if url.endswith(".zip"):
            xml_data = self._parse_zip_xml(web_data)
            # TODO: parse xml data
            pass
        elif url.startswith(self.list_base2_v2_url) and not url.endswith(".json"):
            # TODO: parse 'https://results.elections.qld.gov.au/aurukun2020/01'
            pass
        elif url.startswith(self.list_base_v2_url) and url.endswith(".json"):
            # TODO: parse 'https://resultsdata.elections.qld.gov.au/bundamba2020-status.json'
            pass
        elif url.startswith(self.list_base1_v1_url) and url.endswith(".html"):
            # TODO: parse 'https://results.ecq.qld.gov.au/elections/state/REF2016/results/summary.html'
            pass
        else:
            # TODO: other pages:
            #  'https://results1.elections.qld.gov.au/currumbin2020/02401/state',
            #  'https://www.ecq.qld.gov.au/elections/election-events',
            #  'https://www.ecq.qld.gov.au/elections/election-results/2009-state-election'
            pass
        return []

    def _parse_zip_xml(self, web_data: WebDataAvailable):
        url = web_data.response_url
        with io.BytesIO(web_data.body_raw) as zip_data:
            with ZipFile(zip_data, "r") as zip_reader:
                # zip_test = zip_reader.testzip()
                # if zip_test is not None:
                #     raise ValueError(f"Bad zip file '{url}': {zip_test}")
                file_list = zip_reader.infolist()
                for file_info in file_list:
                    if not file_info.filename.endswith("xml"):
                        continue
                    file_data = zip_reader.read(file_info.filename).decode("utf-8")
                    return xml_to_data(file_data)
