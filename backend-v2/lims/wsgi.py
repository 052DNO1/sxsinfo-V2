"""
WSGI config for lims project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lims.settings.production')
application = get_wsgi_application()
