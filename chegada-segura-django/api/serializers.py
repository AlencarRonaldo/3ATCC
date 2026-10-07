from django.contrib.auth import authenticate
from rest_framework import serializers
from accounts.models import User
from core.models import Student,Guardian,SchoolClass,Enrollment,Arrival,Notification,Correction,AuditLog

class LoginSerializer(serializers.Serializer):
    username=serializers.CharField(); password=serializers.CharField(write_only=True)
    def validate(self,data):
        user=authenticate(username=data['username'],password=data['password'])
        if not user and '@' in data['username']:
            try: user=authenticate(username=User.objects.get(email__iexact=data['username']).username,password=data['password'])
            except User.DoesNotExist: user=None
        if not user or not user.active or not user.is_active: raise serializers.ValidationError('Credenciais inválidas.')
        data['user']=user; return data
class UserSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,required=False)
    class Meta: model=User; fields=['id','username','email','first_name','last_name','role','active','password','date_joined'] ; read_only_fields=['id','date_joined']
    def create(self,validated):
        p=validated.pop('password',None)
        user=User(**validated)
        if p: user.set_password(p)
        else: raise serializers.ValidationError({'password':'Obrigatória.'})
        user.save(); return user
    def update(self,instance,validated):
        p=validated.pop('password',None)
        for k,v in validated.items(): setattr(instance,k,v)
        if p: instance.set_password(p)
        instance.save(); return instance
class StudentSerializer(serializers.ModelSerializer):
    class Meta: model=Student; fields=['id','ra','name','active','created_at','updated_at']; read_only_fields=['id','created_at','updated_at']
class GuardianSerializer(serializers.ModelSerializer):
    class Meta: model=Guardian; fields=['id','student','name','phone_e164','active','created_at','updated_at']; read_only_fields=['id','created_at','updated_at']
class ClassSerializer(serializers.ModelSerializer):
    class Meta: model=SchoolClass; fields=['id','name','shift','start_time','late_after_minute','active','created_at','updated_at']; read_only_fields=['id','created_at','updated_at']
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta: model=Enrollment; fields=['id','student','school_class','starts_on','ends_on','active']; read_only_fields=['id']
class ArrivalSerializer(serializers.ModelSerializer):
    student_name=serializers.CharField(source='student.name',read_only=True); student_ra=serializers.CharField(source='student.ra',read_only=True); class_name=serializers.CharField(source='school_class.name',read_only=True); shift=serializers.CharField(source='school_class.shift',read_only=True); confirmed_by_name=serializers.SerializerMethodField()
    class Meta: model=Arrival; fields=['id','student','student_name','student_ra','school_class','class_name','shift','confirmed_by','confirmed_by_name','recorded_at','school_date','status','source','late_minutes','rule_applied','notes','cancelled_at']; read_only_fields=['id','recorded_at','school_date','status','source','late_minutes','rule_applied','cancelled_at','confirmed_by']
    def get_confirmed_by_name(self,obj): return obj.confirmed_by.get_full_name() or obj.confirmed_by.username
class NotificationSerializer(serializers.ModelSerializer):
    guardian_name=serializers.CharField(source='guardian.name',read_only=True); student_name=serializers.CharField(source='arrival.student.name',read_only=True)
    class Meta: model=Notification; fields=['id','arrival','guardian','guardian_name','student_name','status','attempts','provider_message_id','last_error','next_attempt_at','created_at','updated_at']
class CorrectionSerializer(serializers.ModelSerializer):
    class Meta: model=Correction; fields=['id','arrival','author','action','reason','before_json','after_json','created_at']; read_only_fields=['id','author','before_json','after_json','created_at']
