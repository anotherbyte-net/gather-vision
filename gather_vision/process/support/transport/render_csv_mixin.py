import csv
from typing import Iterable

from django.http import StreamingHttpResponse
from django.utils import timezone

from gather_vision import models as app_models


class RenderCsvMixin:
    class Echo:
        """An object that implements just the write method of the file-like
        interface.
        """

        def write(self, value):
            """Write the value by returning it, instead of storing in a buffer."""
            return value

    def get_data_csv(self, items: Iterable[app_models.TransportItem]):
        time_stamp = timezone.now()
        time_formatted = time_stamp.isoformat(timespec="seconds")
        time_filename = time_formatted.replace(":", "_").replace("+", "_")
        file_name = f"transport-{time_filename}.csv"

        return StreamingHttpResponse(
            self._write_csv(items),
            content_type="text/csv;charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
        )

    def _write_csv(self, items: Iterable[app_models.TransportItem]):
        pseudo_buffer = RenderCsvMixin.Echo()
        csv_headers = app_models.TransportItem.long_csv_headers()
        writer = csv.DictWriter(pseudo_buffer, csv_headers)
        yield writer.writeheader()

        for item in items:
            yield writer.writerow(item.long_csv())
