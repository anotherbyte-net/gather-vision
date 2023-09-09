import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from gather_vision.services.data.manage import FixtureManager, DataLoaderManager

from gather_vision.services.web.client import DownloadClient


class Command(BaseCommand):
    help = (
        "Loads data for gather-vision. "
        "Uses manually-specified data, raw data, and data obtained from the web."
    )

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        logger = logging.getLogger("gathervision.core")
        logger.info("Starting to load gather-vision data.")

        # load all fixtures
        fm = FixtureManager()
        fm.run(settings.FIXTURE_DIRS)

        # load data from files and web
        pref = "gather_vision.services"
        data_loaders = [
            f"{pref}.water.au_bom_river_height.loaders.AuBomRiverHeights",
            f"{pref}.water.au_qld_bcc_waterways.loaders.AuQldBccWaterways",
            f"{pref}.petition.au_parliament.loaders.AuParliamentPetitions",
        ]
        dlm = DataLoaderManager()
        dl_loaders = list(dlm.run(settings.VISION_DATA_DIR, data_loaders))

        # run web loaders
        logger.info(f"Running {len(dl_loaders)} downloaders.")
        dl_client = DownloadClient()
        dl_client.scrapy(*dl_loaders)

        logger.info("Finished loading gather-vision data.")
