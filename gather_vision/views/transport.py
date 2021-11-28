from typing import Optional

from django.http import HttpResponse
from django.utils.html import escape
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import TemplateView


class TransportIndexView(TemplateView):
    template_name = "gather_vision/transport/index.html"
    page_title = _("Transport")


class TransportDataView(View):
    def get(self, request, cust_ext: Optional[str] = None):
        """
        Get the transport data in various formats.
        The available formats are csv, json, ics.

        The format can be selected by:
         - extension in the final path segment
         - querystring 'format'
        """
        available_formats = {
            "txt": "text/plain",
            "json": "application/json",
            "csv": "text/csv",
            "ics": "text/calendar",
        }
        default_format = "txt"

        requested_formats = [cust_ext] + request.GET.getlist("format", [])
        requested_formats = sorted(
            {i.strip(" .").casefold() for i in requested_formats if i and i.strip()}
        )
        if len(requested_formats) > 1:
            return HttpResponse("Too many formats.", status=406)

        if len(requested_formats) < 1:
            requested_formats = [default_format]

        requested_format = requested_formats[0]

        if requested_format not in available_formats:
            msg = escape(f"Format '{requested_format}' is not available.")
            return HttpResponse(msg, status=406)

        media_type = available_formats[requested_format]
        msg = escape(f"Format is '{requested_format}' - '{media_type}'.")
        return HttpResponse(msg)
