import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','chegada_segura.settings')
import django; django.setup()
from django.test import TestCase,override_settings
from rest_framework.test import APIClient
from accounts.models import User
class AuthApiTests(TestCase):
    def test_login_returns_tokens(self):
        User.objects.create_user(username='admin',email='admin@example.com',password='Admin@12345',role='ADMIN')
        c=APIClient(); r=c.post('/api/auth/login/',{'username':'admin','password':'Admin@12345'},format='json')
        self.assertEqual(r.status_code,200); self.assertIn('access',r.data); self.assertIn('refresh',r.data)
    @override_settings(KIOSK_API_KEY='kiosk')
    def test_kiosk_rejects_bad_key(self):
        r=APIClient().get('/api/tablet/student/',{'ra':'1','name':'X'},HTTP_X_KIOSK_KEY='bad')
        self.assertEqual(r.status_code,401)
