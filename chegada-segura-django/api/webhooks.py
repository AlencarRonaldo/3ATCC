import json
from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from core.models import Notification

@require_http_methods(['GET'])
def whatsapp_verify(request):
    mode=request.GET.get('hub.mode'); token=request.GET.get('hub.verify_token'); challenge=request.GET.get('hub.challenge')
    expected=getattr(settings,'WHATSAPP_VERIFY_TOKEN','') or settings.KIOSK_API_KEY
    if mode=='subscribe' and token==expected: return HttpResponse(challenge or '',content_type='text/plain')
    return HttpResponse('Forbidden',status=403)
@csrf_exempt
@require_http_methods(['POST'])
def whatsapp_status(request):
    try: data=json.loads(request.body or '{}')
    except json.JSONDecodeError: return JsonResponse({'error':'invalid_json'},status=400)
    for entry in data.get('entry',[]):
        for change in entry.get('changes',[]):
            value=change.get('value',{})
            for status in value.get('statuses',[]):
                provider_id=status.get('id'); state=status.get('status')
                if not provider_id: continue
                mapped={'sent':'SENT','delivered':'DELIVERED','read':'DELIVERED','failed':'FAILED'}.get(state)
                if mapped: Notification.objects.filter(provider_message_id=provider_id).update(status=mapped,last_error=status.get('errors',[{}])[0].get('title') if state=='failed' and status.get('errors') else None)
    return JsonResponse({'received':True})
