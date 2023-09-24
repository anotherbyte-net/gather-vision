from gather_vision.apps.explore import models as explore_models
from gather_vision.obtain.core import data
from gather_vision.obtain.place.au import area_au

area_qld = data.GatherDataArea(
    title="Queensland Government",
    level=explore_models.Area.LEVEL_REGION,
)
origin_qld = data.GatherDataOrigin(
    title="Queensland Government",
    description="State government for Queensland.",
    url="https://www.qld.gov.au/",
    areas=[area_au, area_qld],
)
