import os
from pathlib import Path
from zoneinfo import ZoneInfo

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from gather_vision.process.component.http_client import HttpClient
from gather_vision.process.component.logger import Logger
from gather_vision.process.manage.contact_tracing import ContactTracing
from gather_vision.process.manage.outages import Outages
from gather_vision.process.manage.petitions import Petitions
from gather_vision.process.manage.playlists import Playlists
from gather_vision.process.manage.transport import Transport


class Command(BaseCommand):
    help = "Run a gather-vision management command."

    _processes = {
        "contacttracing": ContactTracing,
        "outages": Outages,
        "petitions": Petitions,
        "playlists": Playlists,
        "transport": Transport,
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "process",
            choices=sorted(self._processes.keys()),
            help="The name of the process to run.",
        )
        parser.add_argument(
            "operation",
            choices=["init", "import", "update"],
            help="The operation to run.",
        )
        parser.add_argument(
            "timezone",
            type=ZoneInfo,
            help="The name of the timezone to use for dates and times.",
        )
        parser.add_argument(
            "--data-path", type=Path, help="The path to the data file to import."
        )

    def handle(self, *args, **options):
        logger = Logger(stdout=self.stdout, style=self.style)

        http_client = HttpClient(logger)
        process = options["process"]
        operation = options["operation"]
        tz = options["timezone"]
        data_path = options.get("data_path")

        try:
            timezone.activate(tz)
            os.environ["TZ"] = str(tz)

            process_class = self._processes[process]
            process_obj = process_class(logger, tz, http_client)

            attr = f"run_{operation}"
            if not hasattr(process_obj, attr):
                raise ValueError(f"Process '{process}' has no operation '{operation}'.")

            if operation == "import" and not data_path:
                raise ValueError("The data path is required to run import.")

            attr_ref = getattr(process_obj, attr)
            if operation == "init":
                attr_ref()
            elif operation == "import":
                attr_ref(data_path)
            elif operation == "update":
                attr_ref()

            logger.info("Finished.")

        except Exception as e:
            raise CommandError(e)

        finally:
            timezone.deactivate()
