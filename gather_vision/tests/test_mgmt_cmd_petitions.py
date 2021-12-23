import unittest
from io import StringIO

from django.core.management import call_command, CommandError
from django.test import TestCase

from gather_vision import models as app_models
from gather_vision.process.component.metadata import Metadata
from gather_vision.tests.support import (
    mock_http_client_send_request,
    match_output,
    example_data_dir,
    RequestsTestResponse,
)


class ManagementCommandPetitionsTest(TestCase):

    _cmd = "visionprocess"
    _process = "petitions"
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

        can_import = [
            "data.sqlite",
            "data(2).sqlite",
            "data(5).sqlite",
            "data(6).sqlite",
        ]

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
                            ("INFO", "Importing petitions."),
                        ],
                        start=0,
                        stop=3,
                    )
                    if path.name in can_import:
                        match_output(
                            self,
                            stdout_act,
                            [
                                ("INFO", "Finished importing petitions."),
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

        base_url1 = "https://www.parliament.qld.gov.au"
        base_url2 = f"/Work-of-the-Assembly/Petitions/"

        current_args = (
            "GET",
            f"{base_url1}{base_url2}Current-EPetitions",
        )
        current_data = f"""<div class='current-petitions'>
            <div class='petitions-listing'>
                <a href='{base_url2}viewurl1=instanceid1'>title1</a>
                <span class='petitions-listing__subtext'>closed date: 24/12/2021</span>
                <span class='petitions-listing__signatures-highlight'>20 Signatures</span>
            </div>
        </div>"""

        instance_args = ("GET", f"{base_url1}{base_url2}viewurl1=instanceid1")

        instance_data = """
        <div class='petition-details'>
            <h3>title1</h3>
            <span class='petition-details__elegibility'>Eligibility - el1</span>
            <div class='petition-details__petitioner-details-wrapper'>pet1</div>
            <div class='petition-details__signatures'>Total Signatures - 20</div>
            <div class='petition-details__content--body'>body1</div>
            <div class='petition-details__prop'>Sponsoring Member: sponsor1</div>
            <div class='petition-details__prop'>Posting Date: 23/12/2021</div>
            <div class='petition-details__prop'>Closing Date: 24/12/2021</div>
        </div>
        """

        base_url3 = "https://epetitions.brisbane.qld.gov.au/"

        list_args = ("GET", base_url3)
        list_data = """
        <table class='petitions'>
        <tr><th>title</th><th>who</th><th>closed date</th></tr>
        <tr><td><a href='instanceid2'>title2</a></td><td>principal2</td><td>24/12/2021</td></tr>
        </table>"""

        instance2_args = ("GET", f"{base_url3}petition/view/pid/instanceid2")
        instance2_data = """
        <div class='page-title'><h1>title2</h1></div>
        <table class='petition-details'>
        <tr><td>who</td><td>principal2</td></tr>
        <tr><td>closed date</td><td>24/12/2021</td></tr>
        <tr><td>signatures</td><td>signatures 40</td></tr>
        </table>
        <div id='petition-details'>body2</div>
        """

        def http_request_side_effect(*args, **kwargs):
            if args == current_args and not kwargs:
                return RequestsTestResponse(text=current_data)
            elif args == instance_args and not kwargs:
                return RequestsTestResponse(text=instance_data)
            elif args == list_args and not kwargs:
                return RequestsTestResponse(text=list_data)
            elif args == instance2_args and not kwargs:
                return RequestsTestResponse(text=instance2_data)
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
                ("INFO", "Updating Queensland Government petitions."),
                ("INFO", "Petitions 1 (1 created) changes 1 (1 added)."),
                ("INFO", "Finished updating petitions."),
                ("INFO", "Updating Brisbane City Council petitions."),
                ("INFO", "Petitions 1 (1 created) changes 1 (1 added)."),
                ("INFO", "Finished updating petitions."),
                ("INFO", "Finished."),
            ],
        )

        objs = app_models.InformationSource.objects.all()
        self.assertEquals(len(objs), 2)
        self.assertEqual(repr(objs[0]), "<InformationSource: au_qld>")
        self.assertEqual(repr(objs[1]), "<InformationSource: au_qld_bcc>")

        objs = app_models.PetitionItem.objects.all()
        self.assertEquals(len(objs), 2)
        self.assertEqual(repr(objs[0]), '<PetitionItem: Started 2021-12-22: "title1">')
        self.assertEqual(repr(objs[1]), '<PetitionItem: Started None: "title2">')

        objs = app_models.PetitionChange.objects.all()
        self.assertEquals(len(objs), 2)
        self.assertTrue(
            repr(objs[0]).startswith("<PetitionChange: 20 total signatures by ")
        )
        self.assertTrue(
            repr(objs[1]).startswith("<PetitionChange: 40 total signatures by ")
        )
