from pathlib import Path

import pytz
from django.core.management.base import BaseCommand, CommandError

from gather_vision.process.component.logger import Logger
from gather_vision.process.manage.outages import Outages


class Command(BaseCommand):
    help = "Import electricity outage data from a sqlite file."

    def add_arguments(self, parser):
        parser.add_argument("timezone", type=pytz.timezone)
        parser.add_argument("path", type=Path)

    def handle(self, *args, **options):
        logger = Logger(stdout=self.stdout, style=self.style)
        tz = options["timezone"]
        path = options["path"]

        process = Outages(logger, tz)
        try:
            process.import_outages(path)
        except Exception as e:
            raise CommandError(e)
