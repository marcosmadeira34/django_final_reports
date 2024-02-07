from __future__ import absolute_import, unicode_literals

# Certificando que o aplicativo Celery será iniciado quando o Django for iniciado
from .celery import app as celery_app

__all__ = ('celery_app',)