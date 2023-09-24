from gather_vision.apps.explore import models as explore_models
from gather_vision.obtain.core import data


area_au = data.GatherDataArea(
    title="Australian Government",
    level=explore_models.Area.LEVEL_COUNTRY,
)
origin_au = data.GatherDataOrigin(
    title="Australian Government",
    description="Federal government for Australia.",
    url="https://www.australia.gov.au/",
    areas=[area_au],
)
