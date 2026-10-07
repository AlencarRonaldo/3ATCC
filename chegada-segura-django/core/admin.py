from django.contrib import admin
from .models import Student,Guardian,SchoolClass,Enrollment,Arrival,Notification,NotificationAttempt,Correction,AuditLog
for model in [Student,Guardian,SchoolClass,Enrollment,Arrival,Notification,NotificationAttempt,Correction,AuditLog]: admin.site.register(model)
