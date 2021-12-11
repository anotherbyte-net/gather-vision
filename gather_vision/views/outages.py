from datetime import timedelta
from zoneinfo import ZoneInfo

from django.views.generic import TemplateView
from django.utils.translation import gettext as _

from gather_vision import models as app_models
from gather_vision.process.component.time_series import TimeSeries


class OutageIndexView(TemplateView):
    template_name = "gather_vision/outages/index.html"
    page_title = _("Outages")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["graph_data"] = self._graph_data()
        context["graph_layout"] = self._graph_layout()
        context["graph_config"] = self._graph_config()
        return context

    def _graph_data(self):
        # get date range
        date_range = app_models.OutageGroup.get_retrieved_date_range()
        stop_date = date_range.get("max")
        start_date = stop_date - timedelta(days=30 * 12 * 2)
        ts = TimeSeries(start_date, stop_date, ZoneInfo("Australia/Brisbane"))

        # get data
        query = app_models.OutageGroup.get_data_items(start_date, stop_date)
        petition_data = ts.outages(query)
        return petition_data

    def _graph_layout(self):
        return {
            "title": "Electricity Outages and Demand Over Time",
            "xaxis": {
                "autorange": True,
                "rangeselector": {
                    "buttons": [
                        {
                            "count": 1,
                            "label": "1m",
                            "step": "month",
                            "stepmode": "backward",
                        },
                        {
                            "count": 6,
                            "label": "6m",
                            "step": "month",
                            "stepmode": "backward",
                        },
                        {
                            "count": 1,
                            "label": "1y",
                            "step": "year",
                            "stepmode": "backward",
                        },
                        {
                            "step": "all",
                        },
                    ]
                },
                "rangeslider": True,
                "type": "date",
            },
            "yaxis": {
                "title": "Demand and Outage Count",
                "autorange": True,
                "type": "linear",
            },
            "yaxis2": {
                "title": "Rating",
                "autorange": True,
                "overlaying": "y",
                "side": "right",
            },
        }

    def _graph_config(self):
        return {
            "responsive": True,
        }
