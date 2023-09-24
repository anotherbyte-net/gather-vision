from gather_vision.apps.explore import models as explore_models
from gather_vision.obtain.core import data
from gather_vision.obtain.place.au import area_au
from gather_vision.obtain.place.au.qld import area_qld

tz_toowoomba = "Australia/Brisbane"
area_toowoomba_rc = data.GatherDataArea(
    title="Toowoomba Regional Council",
    level=explore_models.Area.LEVEL_DISTRICT,
)
origin_toowoomba = data.GatherDataOrigin(
    title="Toowoomba Regional Council",
    description="Local government for the Toowoomba region "
    "in South East Queensland.",
    url="https://www.tr.qld.gov.au/",
    areas=[area_au, area_qld, area_toowoomba_rc],
)
area_toowoomba = data.GatherDataArea(
    title="Toowoomba City",
    level=explore_models.Area.LEVEL_LOCALITY,
)
