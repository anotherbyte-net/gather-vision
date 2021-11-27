import pytz
from django.core.management.base import BaseCommand, CommandError

from gather_vision.process.component.logger import Logger
from gather_vision.process.manage.playlists import Playlists


class Command(BaseCommand):
    help = "Initialise the music playlist services."

    def add_arguments(self, parser):
        parser.add_argument("timezone", type=pytz.timezone)

    def handle(self, *args, **options):
        logger = Logger(stdout=self.stdout, style=self.style)
        tz = options["timezone"]

        process = Playlists(logger, tz)
        try:
            process.init()
        except Exception as e:
            raise CommandError(e)
