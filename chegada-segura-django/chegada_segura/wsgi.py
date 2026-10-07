import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE','chegada_segura.settings')
application = get_wsgi_application()
