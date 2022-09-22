from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from gather_vision.models import WaterQualitySample


@dataclass
class WaterQualityMeasure:

    site_number: int
    site_name: str
    location_longitude: float
    location_latitude: float
    location_description: str
    observation_date: datetime
    observation_value: Optional[int]
    observation_status: str

    @classmethod
    def build_from_excel(
        cls, site_info: dict, measure_date: datetime, measure_value: Union[str, int]
    ):
        if isinstance(measure_value, int):
            observation_value = measure_value
            observation_status = WaterQualitySample.VALID
        elif str(measure_value or "").strip() == "NT":
            observation_value = None
            observation_status = WaterQualitySample.NOT_TESTED
        elif str(measure_value or "").strip().startswith(">") or str(
            measure_value or ""
        ).strip().startswith("<"):
            observation_value = int(
                str(measure_value or "").strip()[1:].replace(",", ""), base=10
            )
            observation_status = WaterQualitySample.VALID
        else:
            observation_value = None
            observation_status = WaterQualitySample.INVALID

        return WaterQualityMeasure(
            observation_date=measure_date,
            observation_value=observation_value,
            observation_status=observation_status,
            **site_info,
        )

    def __str__(self):
        result = [
            ("num", self.site_number),
            ("site", self.site_name),
            ("location", f"{self.location_longitude},{self.location_latitude}"),
            (
                "date",
                self.observation_date.isoformat() if self.observation_date else "",
            ),
            (
                "value",
                self.observation_value
                if self.observation_value
                else self.observation_status,
            ),
        ]
        return "; ".join(f"{k}={v}" for k, v in result)
