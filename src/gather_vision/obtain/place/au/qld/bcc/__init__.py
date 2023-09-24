from gather_vision.apps.explore import models as explore_models
from gather_vision.obtain.core import data
from gather_vision.obtain.place.au import area_au
from gather_vision.obtain.place.au.qld import area_qld

tz_bne = "Australia/Brisbane"
area_bcc = data.GatherDataArea(
    title="Brisbane City Council",
    level=explore_models.Area.LEVEL_DISTRICT,
)
area_brisbane = data.GatherDataArea(
    title="Brisbane City",
    level=explore_models.Area.LEVEL_LOCALITY,
)
origin_bcc = data.GatherDataOrigin(
    title="Brisbane City Council",
    description="Local government for the Greater Brisbane area "
    "in South East Queensland.",
    url="https://www.brisbane.qld.gov.au/",
    areas=[area_au, area_qld, area_bcc, area_brisbane],
)
