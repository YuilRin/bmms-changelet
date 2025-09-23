"""
WSGI config for bmms_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = str(BASE_DIR / "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmms_api.settings')

application = get_wsgi_application()
