from io import StringIO

from django.core.management import call_command, CommandError
from django.test import TestCase

from gather_vision import models as app_models
from gather_vision.process.component.metadata import Metadata
from gather_vision.tests.support import mock_http_client_send_request, match_output


class ContactTracingTest(TestCase):
    _cmd = "visionprocess"
    _process = "contacttracing"
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

    def test_import(self):
        # arrange
        metadata = Metadata()
        user_agent = f"gather-vision (+{metadata.documentation_url()})"
        stdout = StringIO()
        stderr = StringIO()
        operation = "import"

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

        def http_request_side_effect(*args, **kwargs):
            raise ValueError()

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
                ("INFO", "Finished."),
            ],
        )

        objs = app_models.InformationSource.objects.all()
        self.assertEquals(len(objs), 0)
        # self.assertEqual(repr(objs[0]), "<InformationSource: translink>")
