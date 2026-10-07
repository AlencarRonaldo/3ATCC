from datetime import time,date
from django.core.management.base import BaseCommand
from accounts.models import User
from core.models import Student,Guardian,SchoolClass,Enrollment
class Command(BaseCommand):
    help='Cria dados mínimos para desenvolvimento.'
    def handle(self,*args,**kwargs):
        admin,_=User.objects.get_or_create(username='admin',defaults={'email':'admin@chegadasegura.local','first_name':'Administrador','role':'ADMIN','active':True,'is_staff':True,'is_superuser':True})
        admin.email='admin@chegadasegura.local'; admin.role='ADMIN'; admin.active=True; admin.is_staff=True; admin.is_superuser=True; admin.set_password('Admin@12345'); admin.save()
        cls,_=SchoolClass.objects.get_or_create(name='1A',defaults={'shift':'MORNING','start_time':time(7,0),'late_after_minute':10})
        student,_=Student.objects.get_or_create(ra='100001',defaults={'name':'Aluno Demonstração'})
        Guardian.objects.get_or_create(student=student,name='Responsável Demonstração',defaults={'phone_e164':'+5511999999999','active':True})
        Enrollment.objects.get_or_create(student=student,school_class=cls,starts_on=date.today(),defaults={'active':True})
        self.stdout.write(self.style.SUCCESS('Seed concluído. Login: admin / Admin@12345'))
