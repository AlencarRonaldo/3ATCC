from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from core.models import Notification,NotificationAttempt,NotificationStatus
from .whatsapp import whatsapp_provider

def backoff(attempt): return timedelta(seconds=min(3600,(2**max(0,attempt-1))*30))

def process_notification_batch(limit=None):
    limit=limit or settings.NOTIFICATION_BATCH_SIZE; now=timezone.now(); count=0
    qs=Notification.objects.select_related('guardian','arrival__student','arrival__school_class').filter(status__in=['PENDING','FAILED']).filter(Q(next_attempt_at__isnull=True)|Q(next_attempt_at__lte=now))
    for item in qs.order_by('created_at')[:limit]:
        with transaction.atomic():
            locked=Notification.objects.select_for_update().get(pk=item.pk)
            if locked.status not in ['PENDING','FAILED'] or (locked.next_attempt_at and locked.next_attempt_at>timezone.now()): continue
            locked.status='PROCESSING'; locked.attempts+=1; locked.save(update_fields=['status','attempts','updated_at'])
            attempt=locked.attempts
        try:
            arrival=item.arrival; local=timezone.localtime(arrival.recorded_at)
            result=whatsapp_provider.send_template(to=item.guardian.phone_e164,template_name=settings.WHATSAPP_TEMPLATE_NAME,language=settings.WHATSAPP_TEMPLATE_LANGUAGE,body_parameters=[arrival.student.name,arrival.school_class.name,local.strftime('%H:%M'),f'{arrival.late_minutes} min de atraso' if arrival.status=='LATE' else 'no horário'])
            Notification.objects.filter(pk=item.pk).update(status='SENT',provider_message_id=result['provider_message_id'],last_error=None,next_attempt_at=None)
            NotificationAttempt.objects.create(notification=item,success=True,provider_status=result.get('provider_status'))
        except Exception as exc:
            final=attempt>=settings.NOTIFICATION_MAX_ATTEMPTS
            Notification.objects.filter(pk=item.pk).update(status='FAILED' if final else 'PENDING',last_error=str(exc)[:2000],next_attempt_at=None if final else timezone.now()+backoff(attempt))
            NotificationAttempt.objects.create(notification=item,success=False,error_message=str(exc)[:2000])
        count+=1
    return count
