import unicodedata
from datetime import datetime, date, time
from django.utils import timezone
from django.conf import settings
from core.models import AuditLog

def normalize_name(value):
    value=unicodedata.normalize('NFD', value or '')
    value=''.join(c for c in value if unicodedata.category(c)!='Mn')
    return ' '.join(value.strip().lower().split())

def school_now(): return timezone.localtime(timezone.now())
def school_date(dt=None): return school_now().date() if dt is None else timezone.localtime(dt).date()
def minutes_since_midnight(t): return t.hour*60+t.minute

def audit(user, action, entity, entity_id=None, metadata=None):
    return AuditLog.objects.create(user=user,action=action,entity=entity,entity_id=str(entity_id) if entity_id else None,metadata=metadata)

def model_snapshot(arrival):
    return {'id':str(arrival.id),'student_id':str(arrival.student_id),'class_id':str(arrival.school_class_id),'confirmed_by_id':str(arrival.confirmed_by_id),'recorded_at':arrival.recorded_at.isoformat(),'school_date':arrival.school_date.isoformat(),'status':arrival.status,'source':arrival.source,'late_minutes':arrival.late_minutes,'rule_applied':arrival.rule_applied,'notes':arrival.notes,'cancelled_at':arrival.cancelled_at.isoformat() if arrival.cancelled_at else None}
