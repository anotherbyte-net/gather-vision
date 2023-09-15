import dataclasses
import typing

from gather_vision.obtain.core import data


@dataclasses.dataclass
class BrisbaneCityCouncilWaterQualityItem(data.GatherDataItem):
    pass


@dataclasses.dataclass
class BrisbaneCityCouncilWaterLevelItem(data.GatherDataItem):
    pass


class BrisbaneCityCouncilWaterWebData(data.WebData):
    # water quality
    water_url = "https://www.brisbane.qld.gov.au/clean-and-green/natural-environment-and-water/water/water-quality-monitoring"

    # water levels in dams
    @property
    def tags(self) -> dict[str, str]:
        return {
            "country": "Australia",
            "region": "Queensland",
            "district": "Brisbane City Council",
            "locality": "City of Brisbane",
            "data_source_location": "web",
            "data_source_category": "water",
        }

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.water_url]

    def web_resources(
        self, web_data: data.WebDataAvailable
    ) -> typing.Iterable[typing.Union[str, data.GatherDataItem]]:
        yield None
