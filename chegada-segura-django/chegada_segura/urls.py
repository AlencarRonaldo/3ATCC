from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse

def health(_request):
    return JsonResponse({'status':'ok','service':'chegada-segura'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health),
    path('api/', include('api.urls')),
    path('webhooks/', include('api.webhook_urls')),
]
