import dataclasses
import typing

from gather_vision.obtain.core import data


@dataclasses.dataclass
class BrisbaneCityCouncilGovernmentPersonItem(data.GatherDataItem):
    # people
    pass


@dataclasses.dataclass
class BrisbaneCityCouncilGovernmentSittingDateItem(data.GatherDataItem):
    # sitting dates
    pass


@dataclasses.dataclass
class BrisbaneCityCouncilGovernmentMeetingPersonAttendanceItem(data.GatherDataItem):
    # meeting minutes - attendance?
    pass


@dataclasses.dataclass
class BrisbaneCityCouncilGovernmentMeetingVoteItem(data.GatherDataItem):
    # meeting minutes - votes?
    pass


class BrisbaneCityCouncilGovernmentInfo(data.WebData):
    list_url = ""

    @property
    def tags(self) -> dict[str, str]:
        return {
            "country": "Australia",
            "region": "Queensland",
            "district": "Brisbane City Council",
            "locality": "City of Brisbane",
            "data_source_location": "web",
            "data_source_category": "legislatures",
        }

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.list_url]

    def web_resources(
        self, web_data: data.WebDataAvailable
    ) -> typing.Iterable[typing.Union[str, data.GatherDataItem]]:
        pass
