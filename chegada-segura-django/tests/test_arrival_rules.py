import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','chegada_segura.settings')
import django; django.setup()
from datetime import time,date
from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from core.models import Student,SchoolClass,Enrollment,Guardian,Arrival
from api.services.arrival import create_arrival
class ArrivalRuleTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user(username='func',email='func@example.com',password='x',role='EMPLOYEE')
        self.cls=SchoolClass.objects.create(name='1A',shift='MORNING',start_time=time(7,0),late_after_minute=10)
        self.student=Student.objects.create(ra='1',name='João da Silva')
        Enrollment.objects.create(student=self.student,school_class=self.cls,starts_on=date.today(),active=True)
        Guardian.objects.create(student=self.student,name='Resp',phone_e164='+5511999999999')
    def test_within_tolerance_is_on_time(self):
        now=timezone.make_aware(timezone.datetime.combine(date.today(),time(7,10)))
        a,_=create_arrival(ra='1',name='Joao da Silva',confirmed_by=self.user,recorded_at=now)
        self.assertEqual(a.status,'ON_TIME'); self.assertEqual(a.late_minutes,10)
    def test_after_tolerance_is_late(self):
        now=timezone.make_aware(timezone.datetime.combine(date.today(),time(7,11)))
        a,_=create_arrival(ra='1',name='JOÃO DA SILVA',confirmed_by=self.user,recorded_at=now)
        self.assertEqual(a.status,'LATE'); self.assertEqual(a.late_minutes,11)
    def test_duplicate_is_rejected(self):
        now=timezone.make_aware(timezone.datetime.combine(date.today(),time(7,5)))
        create_arrival(ra='1',name='João da Silva',confirmed_by=self.user,recorded_at=now)
        with self.assertRaises(Exception): create_arrival(ra='1',name='João da Silva',confirmed_by=self.user,recorded_at=now)
