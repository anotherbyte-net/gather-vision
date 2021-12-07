from typing import Iterable

from django.http import JsonResponse

from gather_vision import models as app_models


class RenderJsonMixin:
    def get_data_json(self, items: Iterable[app_models.TransportItem]):
        return JsonResponse({"items": [i.long_dict() for i in items]})
