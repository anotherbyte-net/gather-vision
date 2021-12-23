from datetime import timedelta
from io import StringIO
from zoneinfo import ZoneInfo

from django.core.management import call_command, CommandError
from django.test import TestCase
from django.utils import timezone

from gather_vision import models as app_models
from gather_vision.process.component.metadata import Metadata
from gather_vision.process.service.transport.qld_rail_events import QldRailEvents
from gather_vision.tests.support import (
    mock_http_client_send_request,
    match_output,
    RequestsTestResponse,
)


class OutageTest(TestCase):

    _cmd = "visionprocess"
    _process = "transport"
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

        tz = ZoneInfo(self._tz)

        base_url1 = "https://translink.com.au/service-updates/rss"

        date_now = timezone.now().astimezone(tz)
        date1 = date_now - timedelta(days=10)
        date2 = date_now - timedelta(days=8)
        date3 = date_now - timedelta(days=7)
        date4 = date_now - timedelta(days=6)
        date5 = date_now - timedelta(days=4)
        date6 = date_now - timedelta(days=2)
        date7 = date_now - timedelta(days=11)
        date8 = date_now - timedelta(days=1)

        rss_args = ("GET", base_url1)
        rss_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:slash="http://purl.org/rss/1.0/modules/slash/">
  <channel>
    <title>TransLink service notices feed</title>
    <description>Current and upcoming service notices or the TransLink public transport network</description>
    <pubDate>{date1.strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>
    <generator>Laminas_Feed_Writer 2 (https://getlaminas.org)</generator>
    <link>https://translink.com.au/service-updates</link>
    <atom:link rel="self" type="application/rss+xml" href="https://translink.com.au/service-updates/rss"/>
    <item>
      <title>McKean Street, Caboolture - temporary stop closure</title>
      <description><![CDATA[<ul><li>(Minor) McKean Street, Caboolture - temporary stop closure.  
      Starts affecting: {date2.strftime('%Y-%m-%dT%H:%M:%S%z')[:-2] + ':00'}</li></ul>]]></description>
      <link>https://translink.com.au/updates/14396</link>
      <guid>https://translink.com.au/updates/14396</guid>
      <category><![CDATA[Current]]></category>
      <category><![CDATA[Minor]]></category>
      <slash:comments>0</slash:comments>
    </item>
    <item>
      <title>Long weekend track closure - Beenleigh, Gold Coast and Cleveland lines</title>
      <description><![CDATA[<ul><li>(Major) Long weekend track closure - Beenleigh, Gold Coast and Cleveland lines.  
      Starts affecting: {date3.strftime('%Y-%m-%dT%H:%M:%S%z')[:-2] + ':00'} 
      Finishes affecting: {date4.strftime('%Y-%m-%dT%H:%M:%S%z')[:-2] + ':00'}</li></ul>]]></description>
      <link>https://translink.com.au/updates/66966</link>
      <guid>https://translink.com.au/updates/66966</guid>
      <category><![CDATA[Upcoming]]></category>
      <category><![CDATA[Major]]></category>
      <slash:comments>0</slash:comments>
    </item>
    </channel>
    </rss>
        """.encode(
            "utf-8"
        )

        qld_rail1_args = (
            "GET",
            "https://www.queenslandrail.com.au/forcustomers/trackclosures/12monthcalendar",
        )
        qld_rail1_data = ""

        qld_rail2_args = (
            "POST",
            "https://www.queenslandrail.com.au/SPWebApp/api/ContentQuery/GetItems",
        )
        qld_rail2_kwargs = {
            "json": QldRailEvents.params,
            "headers": QldRailEvents.headers,
        }

        qld_rail2_data = r"""
        "[{\"Title\":\"Narangba to Gympie North\",\"Description\":\"\",\"EventDate\":\"%s\",\"EndDate\":\"%s\",\"ID\":\"2710\",\"TrackClosureName0\":\"<a href=\\\"http://translink.com.au/travel-information/service-notices/196/details\\\" target=\\\"_blank\\\">Narangba to Gympie North</a>\",\"LineAffected\":\";#Caboolture;#Sunshine Coast;#\",\"fRecurrence\":\"False\",\"fAllDayEvent\":,\"WorksInclude\":\"Overhead maintenance, track maintenance\",\"Is_x0020_CRR_x0020_Event\":\"\"},{\"Title\":\"Ipswich to Rosewood\",\"Description\":\"\",\"EventDate\":\"%s\",\"EndDate\":\"%s\",\"ID\":\"2711\",\"TrackClosureName0\":\"<a href=\\\"http://translink.com.au/travel-information/service-notices/596/details\\\" target=\\\"_blank\\\">Ipswich to Rosewood</a>\",\"LineAffected\":\";#Ipswich/Rosewood;#\",\"fRecurrence\":\"False\",\"fAllDayEvent\":,\"WorksInclude\":\"Overhead maintenance, track maintenance\",\"Is_x0020_CRR_x0020_Event\":\"\"}]"
        """ % (
            date5.strftime("%m/%d/%Y %I:%M:%S %p"),
            date6.strftime("%m/%d/%Y %I:%M:%S %p"),
            date7.strftime("%m/%d/%Y %I:%M:%S %p"),
            date8.strftime("%m/%d/%Y %I:%M:%S %p"),
        )

        def http_request_side_effect(*args, **kwargs):
            if args == rss_args and not kwargs:
                return RequestsTestResponse(content=rss_data)
            elif args == qld_rail1_args and not kwargs:
                return RequestsTestResponse(content=qld_rail1_data)
            elif args == qld_rail2_args and kwargs == qld_rail2_kwargs:
                return RequestsTestResponse(text=qld_rail2_data)
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
                ("INFO", "Updating transport notices."),
                ("INFO", "Notices 4 (0 updated, 4 created)."),
                ("INFO", "Finished updating transport notices."),
                ("INFO", "Finished."),
            ],
        )

        objs = app_models.InformationSource.objects.all()
        self.assertEquals(len(objs), 2)
        self.assertEqual(repr(objs[0]), "<InformationSource: translink>")
        self.assertEqual(repr(objs[1]), "<InformationSource: qldrail>")

        objs = app_models.TransportItem.objects.all()
        self.assertEquals(len(objs), 4)
        self.assertEqual(
            repr(objs[0]),
            f'<TransportItem: translink: "McKean Street, Caboolture - temporary stop closure" starting {date2.strftime("%Y-%m-%d")}>',
        )
        self.assertEqual(
            repr(objs[1]),
            f'<TransportItem: translink: "Long weekend track closure - Beenleigh, Gold Coast and Cleveland lines" starting {date3.strftime("%Y-%m-%d")} ending {date4.strftime("%Y-%m-%d")}>',
        )
        self.assertEqual(
            repr(objs[2]),
            f'<TransportItem: qldrail: "Narangba to Gympie North" starting {date5.strftime("%Y-%m-%d")} ending {date6.strftime("%Y-%m-%d")}>',
        )
        self.assertEqual(
            repr(objs[3]),
            f'<TransportItem: qldrail: "Ipswich to Rosewood" starting {date7.strftime("%Y-%m-%d")} ending {date8.strftime("%Y-%m-%d")}>',
        )

        objs = app_models.TransportLine.objects.all()
        self.assertEquals(len(objs), 3)
        self.assertEqual(repr(objs[0]), "<TransportLine: Caboolture>")
        self.assertEqual(repr(objs[1]), "<TransportLine: Sunshine Coast>")
        self.assertEqual(repr(objs[2]), "<TransportLine: Ipswich/Rosewood>")
