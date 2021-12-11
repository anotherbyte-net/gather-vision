from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class TimeSeries:
    """Create data appropriate to use as Plotly trace data."""

    def __init__(self, start_date: datetime, stop_date: datetime, tz: ZoneInfo):
        self.start_date = start_date.astimezone(tz)
        self.stop_date = stop_date.astimezone(tz)
        self.days = (stop_date - start_date).days

    def build_date_range(self):
        def daterange(range_start_date, days):
            for n in range(days):
                yield range_start_date + timedelta(n)

        date_range = daterange(self.start_date, self.days)
        for index, current_date in enumerate(date_range):
            yield index, current_date

    def petitions(self, query):
        # raw = self.build_date_range()
        traces = {}
        for item in query:
            # source_name = item.source.name
            # source_title = item.source.title

            petition_title = item.title
            petition_code = item.code
            # petition_opened_date = item.opened_date
            # petition_closed_date = item.closed_date

            traces[petition_code] = {
                "type": "scatter",
                "mode": "lines",
                "name": petition_title,
                "x": [],
                "y": [],
            }

            x = traces[petition_code]["x"]
            y = traces[petition_code]["y"]

            for change_item in item.signature_changes.all():
                date_key = change_item.retrieved_date.strftime("%Y-%m-%d")
                change_signatures = change_item.signatures

                if date_key not in x:
                    x.append(date_key)
                    y.append(change_signatures)

                else:
                    day_index = x.index(date_key)
                    if y[day_index] < change_signatures:
                        y[day_index] = change_signatures

        result = list(traces.values())
        return result

    def outages(self, query):
        traces = []
        demand = {
            "type": "scatter",
            "mode": "lines",
            "name": "Demand",
            "x": [],
            "y": [],
        }
        rating = {
            "type": "scatter",
            "mode": "lines",
            "name": "Rating",
            "x": [],
            "y": [],
            "yaxis": "y2",
        }
        outages = {
            "type": "scatter",
            "mode": "lines",
            "name": "Customers Affected",
            "x": [],
            "y": [],
        }

        traces = [demand, rating, outages]

        for item in query:
            date_key = item.retrieved_date.strftime("%Y-%m-%d %H:%M:00")
            if date_key not in demand["x"]:
                demand["x"].append(date_key)
                demand["y"].append(item.demand)
            if date_key not in rating["x"]:
                rating["x"].append(date_key)
                rating["y"].append(item.rating)
            if date_key not in outages["x"]:
                outages["x"].append(date_key)
                outages["y"].append(item.total_customers)

        return traces
