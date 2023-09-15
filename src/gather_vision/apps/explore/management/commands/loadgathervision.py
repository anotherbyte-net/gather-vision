import logging

from django.core.management.base import BaseCommand

from gather_vision.obtain import available_web_data
from gather_vision.obtain.core import data


class Command(BaseCommand):
    help = ""

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        logger.info(f"Running {__name__}")

        data_load = data.DataLoad()

        # local
        local_items = data_load.run_local([])
        for local_item in local_items:
            pass

        # web
        web_items = data_load.run_web(available_web_data)
        for web_item in web_items:
            pass
