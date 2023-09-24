import dataclasses
import typing

from gather_vision.obtain.core import data


@dataclasses.dataclass(frozen=True)
class BrisbaneCityCouncilGovernmentPersonItem(data.GatherDataItem):
    # people
    pass


@dataclasses.dataclass(frozen=True)
class BrisbaneCityCouncilGovernmentSittingDateItem(data.GatherDataItem):
    # sitting dates
    pass


@dataclasses.dataclass(frozen=True)
class BrisbaneCityCouncilGovernmentMeetingPersonAttendanceItem(data.GatherDataItem):
    # meeting minutes - attendance?
    pass


@dataclasses.dataclass(frozen=True)
class BrisbaneCityCouncilGovernmentMeetingVoteItem(data.GatherDataItem):
    # meeting minutes - votes?
    pass


class BrisbaneCityCouncilGovernmentWebData(data.WebData):
    list_url = ""

    @property
    def name(self) -> str:
        return "au-qld-bcc-government"

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.list_url]

    def web_resources(
        self, web_data: data.WebDataAvailable
    ) -> typing.Iterable[typing.Union[data.GatherDataRequest, data.GatherDataItem]]:
        yield None
