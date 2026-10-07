from datetime import datetime
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .authentication import ActiveJWTAuthentication
from .permissions import AnyStaff,DirectionOrAdmin,AdminOnly,StaffForTablet
from .serializers import *
from .services.arrival import find_student,create_arrival
from .services.common import audit,model_snapshot,school_date
from .services.dashboard import dashboard
from .services.notifications import process_notification_batch
from core.models import *
from accounts.models import User

class LoginView(APIView):
    permission_classes=[AllowAny]; authentication_classes=[]
    def post(self,request):
        s=LoginSerializer(data=request.data); s.is_valid(raise_exception=True); user=s.validated_data['user']; refresh=RefreshToken.for_user(user); return Response({'access':str(refresh.access_token),'refresh':str(refresh),'user':UserSerializer(user).data})
class MeView(APIView):
    def get(self,request): return Response(UserSerializer(request.user).data)

class TabletStudentView(APIView):
    authentication_classes=[]; permission_classes=[AllowAny]
    def get(self,request):
        if not settings.KIOSK_API_KEY or request.headers.get('X-Kiosk-Key')!=settings.KIOSK_API_KEY: return Response({'error':{'code':'INVALID_KIOSK_KEY','message':'Tablet não autorizado.'}},status=401)
        ra=request.query_params.get('ra','').strip(); name=request.query_params.get('name','').strip()
        if not ra or not name: return Response({'error':{'code':'VALIDATION_ERROR','message':'RA e nome são obrigatórios.'}},status=400)
        student,enrollment=find_student(ra,name)
        return Response({'id':str(student.id),'ra':student.ra,'name':student.name,'class':{'id':str(enrollment.school_class.id),'name':enrollment.school_class.name,'shift':enrollment.school_class.shift,'startTime':enrollment.school_class.start_time.strftime('%H:%M')}})
class TabletCheckInView(APIView):
    permission_classes=[StaffForTablet]
    def post(self,request):
        if not settings.KIOSK_API_KEY or request.headers.get('X-Kiosk-Key')!=settings.KIOSK_API_KEY: return Response({'error':{'code':'INVALID_KIOSK_KEY','message':'Tablet não autorizado.'}},status=401)
        ra=request.data.get('ra',''); name=request.data.get('name','')
        arrival,count=create_arrival(ra=ra,name=name,confirmed_by=request.user,source=ArrivalSource.TABLET,notes=request.data.get('notes'))
        return Response({'arrival':ArrivalSerializer(arrival).data,'notificationCount':count},status=201)

class StudentListCreateView(APIView):
    permission_classes=[DirectionOrAdmin]
    def get(self,request):
        qs=Student.objects.all(); q=request.query_params.get('q');
        if q: qs=qs.filter(Q(name__icontains=q)|Q(ra__icontains=q))
        page=self.paginate_queryset(qs,request); return self.get_paginated_response(StudentSerializer(page,many=True).data) if page is not None else Response(StudentSerializer(qs,many=True).data)
    def paginate_queryset(self,qs,request):
        from .pagination import StandardPagination; self.paginator=StandardPagination(); return self.paginator.paginate_queryset(qs,request,view=self)
    def get_paginated_response(self,data): return self.paginator.get_paginated_response(data)
    def post(self,request): s=StudentSerializer(data=request.data); s.is_valid(raise_exception=True); obj=s.save(); audit(request.user,'STUDENT_CREATED','Student',obj.id); return Response(s.data,status=201)
class StudentDetailView(APIView):
    permission_classes=[DirectionOrAdmin]
    def patch(self,request,pk): obj=get_object_or_404(Student,pk=pk); s=StudentSerializer(obj,data=request.data,partial=True); s.is_valid(raise_exception=True); s.save(); audit(request.user,'STUDENT_UPDATED','Student',obj.id); return Response(s.data)
class StudentHistoryView(APIView):
    permission_classes=[DirectionOrAdmin]
    def get(self,request,pk):
        student=get_object_or_404(Student,pk=pk); qs=Arrival.objects.filter(student=student).select_related('school_class','confirmed_by').order_by('-recorded_at'); return Response(ArrivalSerializer(qs,many=True).data)
class GuardianCreateView(APIView):
    permission_classes=[AnyStaff]
    def post(self,request,student_id):
        get_object_or_404(Student,pk=student_id); data={**request.data,'student':student_id}; s=GuardianSerializer(data=data); s.is_valid(raise_exception=True); obj=s.save(); audit(request.user,'GUARDIAN_CREATED','Guardian',obj.id); return Response(s.data,status=201)
class GuardianDetailView(APIView):
    permission_classes=[AnyStaff]
    def patch(self,request,student_id,guardian_id):
        obj=get_object_or_404(Guardian,pk=guardian_id,student_id=student_id); s=GuardianSerializer(obj,data=request.data,partial=True); s.is_valid(raise_exception=True); s.save(); audit(request.user,'GUARDIAN_UPDATED','Guardian',obj.id); return Response(s.data)

class EnrollmentListCreateView(APIView):
    permission_classes=[DirectionOrAdmin]
    def get(self,request):
        qs=Enrollment.objects.select_related('student','school_class').all().order_by('-starts_on')
        student=request.query_params.get('studentId'); active=request.query_params.get('active')
        if student: qs=qs.filter(student_id=student)
        if active is not None: qs=qs.filter(active=active.lower()=='true')
        return Response(EnrollmentSerializer(qs,many=True).data)
    def post(self,request):
        s=EnrollmentSerializer(data=request.data); s.is_valid(raise_exception=True)
        if s.validated_data.get('ends_on') and s.validated_data['ends_on'] < s.validated_data['starts_on']: return Response({'error':{'code':'VALIDATION_ERROR','message':'ends_on não pode ser anterior a starts_on.'}},status=400)
        obj=s.save(); audit(request.user,'ENROLLMENT_CREATED','Enrollment',obj.id); return Response(s.data,status=201)
class EnrollmentDetailView(APIView):
    permission_classes=[DirectionOrAdmin]
    def patch(self,request,pk):
        obj=get_object_or_404(Enrollment,pk=pk); s=EnrollmentSerializer(obj,data=request.data,partial=True); s.is_valid(raise_exception=True); s.save(); audit(request.user,'ENROLLMENT_UPDATED','Enrollment',obj.id); return Response(s.data)

class ClassListCreateView(APIView):
    permission_classes=[DirectionOrAdmin]
    def get(self,request): return Response(ClassSerializer(SchoolClass.objects.all(),many=True).data)
    def post(self,request): s=ClassSerializer(data=request.data); s.is_valid(raise_exception=True); obj=s.save(); audit(request.user,'CLASS_CREATED','SchoolClass',obj.id); return Response(s.data,status=201)
class ClassDetailView(APIView):
    permission_classes=[DirectionOrAdmin]
    def patch(self,request,pk): obj=get_object_or_404(SchoolClass,pk=pk); s=ClassSerializer(obj,data=request.data,partial=True); s.is_valid(raise_exception=True); s.save(); audit(request.user,'CLASS_UPDATED','SchoolClass',obj.id); return Response(s.data)

class UserListCreateView(APIView):
    permission_classes=[AdminOnly]
    def get(self,request): return Response(UserSerializer(User.objects.all(),many=True).data)
    def post(self,request): s=UserSerializer(data=request.data); s.is_valid(raise_exception=True); obj=s.save(); audit(request.user,'USER_CREATED','User',obj.id); return Response(s.data,status=201)
class UserDetailView(APIView):
    permission_classes=[AdminOnly]
    def patch(self,request,pk): obj=get_object_or_404(User,pk=pk); s=UserSerializer(obj,data=request.data,partial=True); s.is_valid(raise_exception=True); s.save(); audit(request.user,'USER_UPDATED','User',obj.id); return Response(s.data)

class ArrivalListCreateView(APIView):
    permission_classes=[AnyStaff]
    def get(self,request):
        qs=Arrival.objects.select_related('student','school_class','confirmed_by').all()
        date=request.query_params.get('date'); month=request.query_params.get('month'); class_id=request.query_params.get('classId'); shift=request.query_params.get('shift')
        if date: qs=qs.filter(school_date=date)
        if month: qs=qs.filter(school_date__year=int(month[:4]),school_date__month=int(month[5:7]))
        if class_id: qs=qs.filter(school_class_id=class_id)
        if shift: qs=qs.filter(school_class__shift=shift)
        qs=qs.order_by('-recorded_at'); from .pagination import StandardPagination; p=StandardPagination(); page=p.paginate_queryset(qs,request); return p.get_paginated_response(ArrivalSerializer(page,many=True).data)
    def post(self,request):
        # Manual entry: still uses RA+name and server-side class/late rule.
        arrival,count=create_arrival(ra=request.data.get('ra',''),name=request.data.get('name',''),confirmed_by=request.user,source=ArrivalSource.MANUAL,notes=request.data.get('notes')); return Response({'arrival':ArrivalSerializer(arrival).data,'notificationCount':count},status=201)
class ArrivalCorrectionView(APIView):
    permission_classes=[DirectionOrAdmin]
    @transaction.atomic
    def patch(self,request,pk):
        arrival=get_object_or_404(Arrival.objects.select_for_update(),pk=pk); reason=(request.data.get('reason') or '').strip(); action=request.data.get('action')
        if not reason: return Response({'error':{'code':'VALIDATION_ERROR','message':'Justificativa é obrigatória.'}},status=400)
        if action not in ['UPDATE','CANCEL']: return Response({'error':{'code':'VALIDATION_ERROR','message':'action deve ser UPDATE ou CANCEL.'}},status=400)
        before=model_snapshot(arrival)
        if action=='CANCEL': arrival.cancelled_at=timezone.now(); arrival.save(update_fields=['cancelled_at']); Notification.objects.filter(arrival=arrival,status__in=['PENDING','PROCESSING']).update(status='CANCELLED')
        else:
            allowed={'notes','status','late_minutes'}
            if 'status' in request.data and request.data['status'] not in [x[0] for x in ArrivalStatus.choices]:
                return Response({'error':{'code':'VALIDATION_ERROR','message':'status inválido.'}},status=400)
            if 'late_minutes' in request.data:
                try:
                    minutes=int(request.data['late_minutes'])
                    if minutes < 0: raise ValueError
                    request.data['late_minutes']=minutes
                except (TypeError,ValueError):
                    return Response({'error':{'code':'VALIDATION_ERROR','message':'late_minutes deve ser um inteiro não negativo.'}},status=400)
            for key in allowed:
                if key in request.data: setattr(arrival,key,request.data[key])
            arrival.save()
        after=model_snapshot(arrival); Correction.objects.create(arrival=arrival,author=request.user,action=action,reason=reason,before_json=before,after_json=after); audit(request.user,'ARRIVAL_CORRECTED','Arrival',arrival.id,{'action':action,'reason':reason}); return Response(ArrivalSerializer(arrival).data)

class DashboardView(APIView):
    permission_classes=[DirectionOrAdmin]
    def get(self,request):
        qs=Arrival.objects.all(); date=request.query_params.get('date'); month=request.query_params.get('month'); class_id=request.query_params.get('classId'); shift=request.query_params.get('shift')
        if date: qs=qs.filter(school_date=date)
        elif month: qs=qs.filter(school_date__year=int(month[:4]),school_date__month=int(month[5:7]))
        else: qs=qs.filter(school_date=school_date())
        if class_id: qs=qs.filter(school_class_id=class_id)
        if shift: qs=qs.filter(school_class__shift=shift)
        return Response(dashboard(qs))
class NotificationListView(APIView):
    permission_classes=[DirectionOrAdmin]
    def get(self,request):
        qs=Notification.objects.select_related('guardian','arrival__student').all().order_by('-created_at'); st=request.query_params.get('status');
        if st: qs=qs.filter(status=st)
        from .pagination import StandardPagination; p=StandardPagination(); page=p.paginate_queryset(qs,request); return p.get_paginated_response(NotificationSerializer(page,many=True).data)
class NotificationProcessView(APIView):
    permission_classes=[DirectionOrAdmin]
    def post(self,request): return Response({'processed':process_notification_batch()})
