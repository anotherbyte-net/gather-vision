import dataclasses
import typing

from gather_vision.plugin import data


@dataclasses.dataclass
class QueenslandEnergexElectricityItem:
    pass


class QueenslandEnergexElectricity(data.WebData):
    demand_min = 0
    demand_max = 5500

    base_url = "https://www.energex.com.au"
    demand_url = f"{base_url}/static/Energex/Network%20Demand/networkdemand.txt"

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.list_url]

    def parse_response(
        self, data: data.WebDataAvailable
    ) -> typing.Generator[typing.Union[str, data.IsDataclass], typing.Any, typing.Any]:
        pass


@dataclasses.dataclass
class QueenslandErgonEnergyElectricityItem:
    pass


class QueenslandErgonEnergyElectricity(data.WebData):
    # "high"
    category_high_max = 5000
    category_high_min = 2000

    # "low"
    category_low_max = 1499
    category_low_min = 0

    # otherwise: "moderate"
    base_url = "https://www.ergon.com.au"
    demand_url = f"{base_url}/static/Ergon/Network%20Demand/currentdemand.json"

    # {"db_connection":"ok","db_query":"ok","data":[
    # {"currentdemand":{"data":"1090.739","time":"2022-09-24 14:12:32.000"}}
    # ]}

    def initial_urls(self) -> typing.Iterable[str]:
        return [self.list_url]

    def parse_response(
        self, data: data.WebDataAvailable
    ) -> typing.Generator[typing.Union[str, data.IsDataclass], typing.Any, typing.Any]:
        pass
