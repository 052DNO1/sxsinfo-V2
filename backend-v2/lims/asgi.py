"""
ASGI config for lims project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.production')
application = get_asgi_application()
