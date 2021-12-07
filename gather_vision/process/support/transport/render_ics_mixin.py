from datetime import datetime, time
from typing import Iterable

from django.http import HttpResponse
from django.utils import timezone

from gather_vision import models as app_models
from gather_vision.process.component.ical import ICal


class RenderIcsMixin:
    def get_data_ics(self, items: Iterable[app_models.TransportItem]):
        time_stamp = timezone.now()
        time_formatted = time_stamp.isoformat(timespec="seconds")
        time_filename = time_formatted.replace(":", "_").replace("+", "_")
        file_name = f"transport-{time_filename}.ics"

        return HttpResponse(
            self._write_ics(items),
            content_type="text/plain;charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
        )

    def _write_ics(self, items: Iterable[app_models.TransportItem]):
        calendar = ICal(
            provider="gather-vision",
            title="Public Transport Notices",
            description="Changes and closures in the public transport network.",
            tz="Australia/Brisbane",
            ttl="PT6H",
        )

        for item in items:
            calendar.add_event(
                title=item.title,
                body=item.body,
                date_start=datetime.combine(item.start_date, time.min),
                date_stop=datetime.combine(item.stop_date or item.start_date, time.max),
                location="",
                url=item.view_url or "",
                uid="-".join([item.source.name, item.source_identifier]),
                date_stamp=item.modified_date,
                date_modified=item.modified_date,
                date_created=item.created_date,
                # sequence_num="",
            )

        cal = calendar.get_calendar()
        cal_str = cal.to_ical()
        return cal_str
