"""
ASGI config for gather-vision project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "gather_vision.proj.settings",
)
os.environ.setdefault(
    "SCRAPY_SETTINGS_MODULE",
    "gather_vision.proj.settings_scrapy",
)

application = get_asgi_application()
