from datetime import datetime, time
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import APIException
from core.models import Student, Enrollment, Arrival, Guardian, Notification, ArrivalSource, ArrivalStatus
from .common import normalize_name, minutes_since_midnight, school_date, audit

class DomainError(APIException):
    status_code=400
    default_code='DOMAIN_ERROR'

def active_enrollment(student, when):
    d=timezone.localtime(when).date()
    return Enrollment.objects.select_related('school_class').filter(student=student,active=True,school_class__active=True,starts_on__lte=d).filter(Q(ends_on__isnull=True)|Q(ends_on__gte=d)).order_by('-starts_on').first()

def find_student(ra,name,when=None):
    when=when or timezone.now()
    try: student=Student.objects.get(ra=ra)
    except Student.DoesNotExist: raise DomainError('Aluno não encontrado ou inativo.')
    if not student.active: raise DomainError('Aluno não encontrado ou inativo.')
    if normalize_name(student.name)!=normalize_name(name):
        e=DomainError('RA e nome não conferem com o cadastro.'); e.status_code=422; e.default_code='STUDENT_NAME_MISMATCH'; raise e
    enrollment=active_enrollment(student,when)
    if not enrollment: e=DomainError('Aluno sem turma ativa.'); e.status_code=409; e.default_code='NO_ACTIVE_ENROLLMENT'; raise e
    return student,enrollment

@transaction.atomic
def create_arrival(*,ra,name,confirmed_by,source=ArrivalSource.TABLET,recorded_at=None,notes=None):
    recorded_at=recorded_at or timezone.now()
    student,enrollment=find_student(ra,name,recorded_at)
    cls=enrollment.school_class
    local=timezone.localtime(recorded_at); actual=local.hour*60+local.minute
    expected=minutes_since_midnight(cls.start_time)
    delay=max(0,actual-expected)
    late=delay>cls.late_after_minute
    status=ArrivalStatus.LATE if late else ArrivalStatus.ON_TIME
    sd=local.date()
    rule=f'Turma {cls.name}: início {cls.start_time.strftime("%H:%M")}, tolerância {cls.late_after_minute} min; atraso calculado {delay} min.'
    if Arrival.objects.filter(student=student,school_date=sd).exists():
        e=DomainError('A chegada deste aluno já foi registrada hoje.'); e.status_code=409; e.default_code='ARRIVAL_ALREADY_EXISTS'; raise e
    try:
        arrival=Arrival.objects.create(student=student,school_class=cls,confirmed_by=confirmed_by,recorded_at=recorded_at,school_date=sd,status=status,source=source,late_minutes=delay,rule_applied=rule,notes=notes)
    except IntegrityError:
        e=DomainError('A chegada deste aluno já foi registrada hoje.'); e.status_code=409; e.default_code='ARRIVAL_ALREADY_EXISTS'; raise e
    guardians=list(Guardian.objects.filter(student=student,active=True))
    Notification.objects.bulk_create([Notification(arrival=arrival,guardian=g,status='PENDING',next_attempt_at=recorded_at) for g in guardians])
    audit(confirmed_by,'ARRIVAL_CREATED','Arrival',arrival.id,{'source':source,'school_date':sd.isoformat(),'status':status})
    return arrival,len(guardians)
