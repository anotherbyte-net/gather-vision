from typing import Optional

from django.http import HttpResponse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import TemplateView

from gather_vision.process.support.select_format_mixin import SelectFormatMixin
from gather_vision.process.support.transport.render_csv_mixin import RenderCsvMixin
from gather_vision.process.support.transport.render_ics_mixin import RenderIcsMixin
from gather_vision.process.support.transport.render_json_mixin import RenderJsonMixin
from gather_vision.process.support.transport.render_txt_mixin import RenderTxtMixin
from gather_vision import models as app_models


class TransportIndexView(TemplateView):
    template_name = "gather_vision/transport/index.html"
    page_title = _("Transport")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "transport_filter" not in context or not context["transport_filter"]:
            context["transport_filter"] = "all"

        transport_filter = context["transport_filter"]
        available = app_models.TransportItem.get_items_available()
        if transport_filter not in available:
            context["items"] = []
        else:
            context["items"] = available[transport_filter]()

        return context


class TransportDataView(
    RenderCsvMixin,
    RenderIcsMixin,
    RenderJsonMixin,
    RenderTxtMixin,
    SelectFormatMixin,
    View,
):
    def get(
        self,
        request,
        transport_filter: Optional[str] = None,
        cust_ext: Optional[str] = None,
    ):
        """
        Get the transport data in various formats.
        The available formats are csv, json, ics.

        The format can be selected by the extension in the final path segment.
        """

        selected_format = self.select_format(cust_ext)

        if selected_format["status_code"] != 200:
            return HttpResponse(
                selected_format["message"], status=selected_format["status_code"]
            )

        if not transport_filter:
            transport_filter = "all"

        available = app_models.TransportItem.get_items_available()
        if transport_filter not in available:
            data = []
        else:
            data = available[transport_filter]()

        if selected_format["extension"] == "csv":
            response = self.get_data_csv(data)
        elif selected_format["extension"] == "ics":
            response = self.get_data_ics(data)
        elif selected_format["extension"] == "json":
            response = self.get_data_json(data)
        elif selected_format["extension"] == "txt":
            response = self.get_data_txt(data)
        else:
            response = HttpResponse("Invalid format.", status=400)

        return response
