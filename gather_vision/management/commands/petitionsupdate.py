import pytz
from django.core.management.base import BaseCommand, CommandError

from gather_vision.process.component.logger import Logger
from gather_vision.process.manage.petitions import Petitions


class Command(BaseCommand):
    help = "Bring in new petition records."

    def add_arguments(self, parser):
        parser.add_argument("timezone", type=pytz.timezone)

    def handle(self, *args, **options):
        logger = Logger(stdout=self.stdout, style=self.style)
        tz = options["timezone"]

        process = Petitions(logger, tz)
        try:
            process.update_petitions()
        except Exception as e:
            raise CommandError(e)
