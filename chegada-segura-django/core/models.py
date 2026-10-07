import uuid
from django.conf import settings
from django.db import models
class Shift(models.TextChoices):
    MORNING='MORNING','Manhã'; AFTERNOON='AFTERNOON','Tarde'; NIGHT='NIGHT','Noite'
class ArrivalStatus(models.TextChoices):
    ON_TIME='ON_TIME','No horário'; LATE='LATE','Atrasado'; MANUAL='MANUAL','Manual'
class ArrivalSource(models.TextChoices):
    TABLET='TABLET','Tablet'; MANUAL='MANUAL','Manual'
class NotificationStatus(models.TextChoices):
    PENDING='PENDING','Pendente'; PROCESSING='PROCESSING','Processando'; SENT='SENT','Enviada'; DELIVERED='DELIVERED','Entregue'; FAILED='FAILED','Falhou'; CANCELLED='CANCELLED','Cancelada'
class CorrectionAction(models.TextChoices):
    UPDATE='UPDATE','Atualização'; CANCEL='CANCEL','Cancelamento'
class Student(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); ra=models.CharField(max_length=40,unique=True); name=models.CharField(max_length=180); active=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['name']
    def __str__(self): return f'{self.ra} - {self.name}'
class Guardian(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name='guardians'); name=models.CharField(max_length=180); phone_e164=models.CharField(max_length=20); active=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: indexes=[models.Index(fields=['student','active'])]
class SchoolClass(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); name=models.CharField(max_length=100); shift=models.CharField(max_length=20,choices=Shift.choices); start_time=models.TimeField(); late_after_minute=models.PositiveIntegerField(default=0); active=models.BooleanField(default=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: indexes=[models.Index(fields=['shift','active'])]; ordering=['name']
class Enrollment(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name='enrollments'); school_class=models.ForeignKey(SchoolClass,on_delete=models.PROTECT,related_name='enrollments'); starts_on=models.DateField(); ends_on=models.DateField(null=True,blank=True); active=models.BooleanField(default=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['student','school_class','starts_on'],name='uniq_enrollment_start')]
        indexes=[models.Index(fields=['student','active']),models.Index(fields=['school_class','active'])]
class Arrival(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); student=models.ForeignKey(Student,on_delete=models.PROTECT,related_name='arrivals'); school_class=models.ForeignKey(SchoolClass,on_delete=models.PROTECT,related_name='arrivals'); confirmed_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='confirmed_arrivals'); recorded_at=models.DateTimeField(); school_date=models.DateField(); status=models.CharField(max_length=20,choices=ArrivalStatus.choices); source=models.CharField(max_length=20,choices=ArrivalSource.choices); late_minutes=models.PositiveIntegerField(default=0); rule_applied=models.TextField(); notes=models.TextField(null=True,blank=True); cancelled_at=models.DateTimeField(null=True,blank=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['student','school_date'],name='uniq_student_school_date')]
        indexes=[models.Index(fields=['school_date']),models.Index(fields=['school_class','school_date']),models.Index(fields=['status','school_date'])]
class Notification(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); arrival=models.ForeignKey(Arrival,on_delete=models.CASCADE,related_name='notifications'); guardian=models.ForeignKey(Guardian,on_delete=models.PROTECT,related_name='notifications'); status=models.CharField(max_length=20,choices=NotificationStatus.choices,default=NotificationStatus.PENDING); attempts=models.PositiveIntegerField(default=0); provider_message_id=models.CharField(max_length=255,null=True,blank=True); last_error=models.TextField(null=True,blank=True); next_attempt_at=models.DateTimeField(null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['arrival','guardian'],name='uniq_arrival_guardian')]
        indexes=[models.Index(fields=['status','next_attempt_at'])]
class NotificationAttempt(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); notification=models.ForeignKey(Notification,on_delete=models.CASCADE,related_name='attempt_logs'); attempted_at=models.DateTimeField(auto_now_add=True); success=models.BooleanField(); provider_status=models.CharField(max_length=80,null=True,blank=True); error_message=models.TextField(null=True,blank=True)
    class Meta: indexes=[models.Index(fields=['notification','attempted_at'])]
class Correction(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); arrival=models.ForeignKey(Arrival,on_delete=models.CASCADE,related_name='corrections'); author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='corrections'); action=models.CharField(max_length=20,choices=CorrectionAction.choices); reason=models.TextField(); before_json=models.JSONField(); after_json=models.JSONField(); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: indexes=[models.Index(fields=['arrival','created_at'])]
class AuditLog(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False); user=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name='audit_logs'); action=models.CharField(max_length=100); entity=models.CharField(max_length=100); entity_id=models.CharField(max_length=100,null=True,blank=True); metadata=models.JSONField(null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: indexes=[models.Index(fields=['entity','entity_id','created_at'])]
