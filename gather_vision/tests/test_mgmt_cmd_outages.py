import unittest
from io import StringIO
from zoneinfo import ZoneInfo

from django.core.management import call_command, CommandError
from django.test import TestCase
from django.utils import timezone

from gather_vision import models as app_models
from gather_vision.process.component.metadata import Metadata
from gather_vision.tests.support import (
    mock_http_client_send_request,
    match_output,
    example_data_dir,
    RequestsTestResponse,
)


class ManagementCommandOutageTest(TestCase):

    _cmd = "visionprocess"
    _process = "outages"
    _tz = "Australia/Melbourne"

    def test_init(self):
        # arrange
        metadata = Metadata()
        user_agent = f"gather-vision (+{metadata.documentation_url()})"

        stdout = StringIO()
        stderr = StringIO()

        operation = "init"

        def http_request_side_effect(*args, **kwargs):
            raise ValueError()

        with_raises = self.assertRaisesMessage(
            CommandError, f"Process '{self._process}' has no operation '{operation}'."
        )
        with_http = mock_http_client_send_request(http_request_side_effect)

        with with_http, with_raises:
            # act
            call_command(
                self._cmd,
                self._process,
                operation,
                self._tz,
                stdout=stdout,
                stderr=stderr,
            )

        # assert
        match_output(self, stderr.getvalue(), [])
        match_output(
            self,
            stdout.getvalue(),
            [
                ("DEBUG", f"User agent set to '{user_agent}'."),
                ("DEBUG", "Using external http client cache 'default'."),
            ],
        )

    def test_import_no_path(self):
        # arrange
        metadata = Metadata()
        user_agent = f"gather-vision (+{metadata.documentation_url()})"
        stdout = StringIO()
        stderr = StringIO()
        operation = "import"

        def http_request_side_effect(*args, **kwargs):
            raise ValueError()

        with_raises = self.assertRaisesMessage(
            CommandError, f"The data path is required to run {operation}."
        )
        with_http = mock_http_client_send_request(http_request_side_effect)

        with with_http, with_raises:
            # act
            call_command(
                self._cmd,
                self._process,
                operation,
                self._tz,
                stdout=stdout,
                stderr=stderr,
            )

        # assert
        match_output(self, stderr.getvalue(), [])
        match_output(
            self,
            stdout.getvalue(),
            [
                ("DEBUG", f"User agent set to '{user_agent}'."),
                ("DEBUG", "Using external http client cache 'default'."),
            ],
        )

    @unittest.skip("Takes a while to run")
    def test_import_with_path(self):
        # arrange
        metadata = Metadata()
        user_agent = f"gather-vision (+{metadata.documentation_url()})"
        stdout = StringIO()
        stderr = StringIO()
        operation = "import"

        def http_request_side_effect(*args, **kwargs):
            raise ValueError()

        with_http = mock_http_client_send_request(http_request_side_effect)

        can_import = ["data(3).sqlite", "data(4).sqlite"]

        # act
        with with_http:
            for path in example_data_dir().iterdir():
                if not path.is_file() or path.suffix != ".sqlite":
                    continue
                with self.subTest(file_name=path.name):

                    command_name = self._cmd
                    args = [
                        self._process,
                        operation,
                        self._tz,
                        "--data-path",
                        str(path),
                    ]
                    options = {"stdout": stdout, "stderr": stderr}

                    if path.name not in can_import:
                        with self.assertRaisesRegex(
                            CommandError, "^Unrecognised data format: .*"
                        ):
                            call_command(command_name, *args, **options)
                    else:
                        call_command(command_name, *args, **options)

                    # assert
                    match_output(self, stderr.getvalue(), [])

                    stdout_act = stdout.getvalue()
                    match_output(
                        self,
                        stdout_act,
                        [
                            ("DEBUG", f"User agent set to '{user_agent}'."),
                            ("DEBUG", "Using external http client cache 'default'."),
                            ("INFO", "Importing outages."),
                        ],
                        start=0,
                        stop=3,
                    )
                    if path.name in can_import:
                        match_output(
                            self,
                            stdout_act,
                            [
                                ("INFO", "Finished importing outages."),
                                ("INFO", "Finished."),
                            ],
                            start=-2,
                        )

    def test_incorrect(self):
        # arrange
        stdout = StringIO()
        stderr = StringIO()

        operation = "incorrect"

        def http_request_side_effect(*args, **kwargs):
            raise ValueError()

        with_raises = self.assertRaisesMessage(
            CommandError,
            f"Error: argument operation: invalid choice: '{operation}' "
            "(choose from 'init', 'import', 'update')",
        )
        with_http = mock_http_client_send_request(http_request_side_effect)

        with with_http, with_raises:
            # act
            call_command(
                self._cmd,
                self._process,
                operation,
                self._tz,
                stdout=stdout,
                stderr=stderr,
            )

        # assert
        match_output(self, stderr.getvalue(), [])
        match_output(self, stdout.getvalue(), [])

    def test_update(self):
        # arrange
        metadata = Metadata()
        user_agent = f"gather-vision (+{metadata.documentation_url()})"
        stdout = StringIO()
        stderr = StringIO()
        operation = "update"

        tz = ZoneInfo(self._tz)
        date_now = timezone.now().astimezone(tz)
        date_now_str = date_now.strftime("%Y-%m-%d")

        base_url = "https://www.energex.com.au/"

        demand_args = (
            "GET",
            f"{base_url}static/Energex/Network%20Demand/networkdemand.txt",
        )
        network_demand = "2057"

        summary_args = ("GET", f"{base_url}api/outages/v0.3/summary")

        def summary_data():
            return {
                "data": {
                    "totalCustomersAffected": 123,
                    "lastUpdated": "2021-12-23 10:10:10",
                }
            }

        council_args = ("GET", f"{base_url}api/outages/v0.3/council")
        council_kwargs = {"params": {"council": ""}}

        def council_data():
            return {"data": [{"name": "council1"}]}

        suburb_args = ("GET", f"{base_url}api/outages/v0.3/suburb")
        suburb_kwargs = {"params": {"council": "council1", "suburb": ""}}

        def suburb_data():
            return {"data": [{"name": "suburb1"}]}

        search_args = ("GET", "https://www.energex.com.au/api/outages/v0.3/search")
        search_kwargs = {"params": {"suburb": "suburb1"}}

        def search_data():
            return {
                "data": [
                    {
                        "restoreTime": "2021-12-24T101010+1000",
                        "streets": ["street1"],
                        "event": "event1",
                        "council": "council1",
                        "suburb": "suburb1",
                        "postcode": "1234",
                        "customersAffected": "50",
                        "cause": "cause1",
                    }
                ]
            }

        def http_request_side_effect(*args, **kwargs):
            if args == demand_args and not kwargs:
                return RequestsTestResponse(text=network_demand)
            elif args == summary_args and not kwargs:
                return RequestsTestResponse(json=summary_data)
            elif args == council_args and kwargs == council_kwargs:
                return RequestsTestResponse(json=council_data)
            elif args == suburb_args and kwargs == suburb_kwargs:
                return RequestsTestResponse(json=suburb_data)
            elif args == search_args and kwargs == search_kwargs:
                return RequestsTestResponse(json=search_data)
            else:
                raise ValueError(f"args: '{args}'; kwargs: '{kwargs}'.")

        with mock_http_client_send_request(http_request_side_effect):
            # act
            call_command(
                self._cmd,
                self._process,
                operation,
                self._tz,
                stdout=stdout,
                stderr=stderr,
            )

        # assert
        match_output(self, stderr.getvalue(), [])
        match_output(
            self,
            stdout.getvalue(),
            [
                ("DEBUG", f"User agent set to '{user_agent}'."),
                ("DEBUG", "Using external http client cache 'default'."),
                ("INFO", "Updating outages."),
                ("INFO", "Groups 1 (1 imported) total items 1 (1 imported)."),
                ("INFO", "Finished updating outages."),
                ("INFO", "Finished."),
            ],
        )

        objs = app_models.InformationSource.objects.all()
        self.assertEquals(len(objs), 1)
        self.assertEqual(repr(objs[0]), "<InformationSource: energex>")

        objs = app_models.OutageGroup.objects.all()
        self.assertEquals(len(objs), 1)
        self.assertEqual(
            repr(objs[0]), f"<OutageGroup: 123 customers affected on {date_now_str}>"
        )

        objs = app_models.OutageItem.objects.all()
        self.assertEquals(len(objs), 1)
        self.assertEquals(
            repr(objs[0]),
            "<OutageItem: event1 caused by cause1 restored on 2021-12-24 00:10:10+00:00>",
        )
