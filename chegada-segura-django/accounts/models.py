import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN='ADMIN','Administrador'; DIRECTION='DIRECTION','Direção'; EMPLOYEE='EMPLOYEE','Funcionário'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    role=models.CharField(max_length=20,choices=Role.choices,default=Role.EMPLOYEE)
    active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    email=models.EmailField(unique=True)
    REQUIRED_FIELDS=['email']; USERNAME_FIELD='username'
    def __str__(self): return self.get_full_name() or self.username
