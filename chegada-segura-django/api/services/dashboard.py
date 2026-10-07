from django.db.models import Count,Avg,Q
from core.models import Arrival,Notification

def dashboard(qs):
    active=qs.filter(cancelled_at__isnull=True)
    total=active.count(); distinct=active.values('student_id').distinct().count(); late=active.filter(status='LATE').count()
    avg=active.filter(status='LATE').aggregate(v=Avg('late_minutes'))['v'] or 0
    pending=Notification.objects.filter(arrival__in=active,status__in=['PENDING','PROCESSING']).count()
    failed=Notification.objects.filter(arrival__in=active,status='FAILED').count()
    by_class=list(active.values('school_class__id','school_class__name','school_class__shift').annotate(occurrences=Count('id'),students=Count('student_id',distinct=True)).order_by('school_class__name'))
    daily=list(active.values('school_date').annotate(occurrences=Count('id'),students=Count('student_id',distinct=True),late=Count('id',filter=Q(status='LATE'))).order_by('school_date'))
    return {'occurrences':total,'distinct_students':distinct,'late_occurrences':late,'average_late_minutes':round(float(avg),2),'notifications_pending':pending,'notifications_failed':failed,'by_class':by_class,'daily_evolution':daily}
