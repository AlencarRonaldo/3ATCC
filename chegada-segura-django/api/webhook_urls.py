from django.urls import path
from .webhooks import whatsapp_verify,whatsapp_status
urlpatterns=[path('whatsapp/',whatsapp_verify),path('whatsapp/status/',whatsapp_status)]
