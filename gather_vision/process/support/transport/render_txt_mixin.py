import os
from typing import Iterable

from django.http import StreamingHttpResponse
from django.utils import timezone

from gather_vision import models as app_models


class RenderTxtMixin:
    def get_data_txt(self, items: Iterable[app_models.TransportItem]):
        time_stamp = timezone.now()
        time_formatted = time_stamp.isoformat(timespec="seconds")
        time_filename = time_formatted.replace(":", "_").replace("+", "_")
        file_name = f"transport-{time_filename}.txt"
        return StreamingHttpResponse(
            (item.long_str() + os.linesep for item in items),
            content_type="text/plain;charset=utf-8",
            headers={"Content-Disposition": f'filename="{file_name}"'},
        )
