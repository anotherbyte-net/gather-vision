"""
WSGI config for gather-vision project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "gather_vision.proj.settings",
)
os.environ.setdefault(
    "SCRAPY_SETTINGS_MODULE",
    "gather_vision.proj.settings_scrapy",
)

application = get_wsgi_application()
