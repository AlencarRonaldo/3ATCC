import os
from pathlib import Path
from datetime import timedelta
from urllib.parse import urlparse
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

def env_bool(name, default=False):
    return os.getenv(name, str(default)).lower() in {'1','true','yes','on'}

def env_list(name, default=''):
    return [x.strip() for x in os.getenv(name, default).split(',') if x.strip()]

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-change-me')
DEBUG = env_bool('DEBUG', True)
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')
TIME_ZONE = os.getenv('TIME_ZONE', 'America/Sao_Paulo')
USE_TZ = True
LANGUAGE_CODE = 'pt-br'

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'rest_framework','django_filters','accounts','core','api',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'chegada_segura.urls'
TEMPLATES = [{
    'BACKEND':'django.template.backends.django.DjangoTemplates',
    'DIRS':[], 'APP_DIRS':True,
    'OPTIONS':{'context_processors':[
        'django.template.context_processors.request','django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages']},
}]
WSGI_APPLICATION = 'chegada_segura.wsgi.application'
ASGI_APPLICATION = 'chegada_segura.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME','chegada_segura'),
        'USER': os.getenv('DB_USER','chegada'),
        'PASSWORD': os.getenv('DB_PASSWORD','chegada'),
        'HOST': os.getenv('DB_HOST','localhost'),
        'PORT': os.getenv('DB_PORT','5432'),
    }
}
# Local tests/development can opt into SQLite explicitly.
if os.getenv('DATABASE_ENGINE','').lower() == 'sqlite3':
    DATABASES['default'] = {'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
]
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_CHARSET = 'utf-8'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('api.authentication.ActiveJWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend','rest_framework.filters.OrderingFilter'),
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_MINUTES','30'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('JWT_REFRESH_DAYS','1'))),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

KIOSK_API_KEY = os.getenv('KIOSK_API_KEY','')
WHATSAPP_ENABLED = env_bool('WHATSAPP_ENABLED', False)
WHATSAPP_API_VERSION = os.getenv('WHATSAPP_API_VERSION','v23.0')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID','')
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN','')
WHATSAPP_TEMPLATE_NAME = os.getenv('WHATSAPP_TEMPLATE_NAME','chegada_segura_chegada')
WHATSAPP_TEMPLATE_LANGUAGE = os.getenv('WHATSAPP_TEMPLATE_LANGUAGE','pt_BR')
WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN','')
NOTIFICATION_MAX_ATTEMPTS = int(os.getenv('NOTIFICATION_MAX_ATTEMPTS','5'))
NOTIFICATION_BATCH_SIZE = int(os.getenv('NOTIFICATION_BATCH_SIZE','20'))

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', True)
