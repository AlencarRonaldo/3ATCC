from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *
urlpatterns=[
 path('auth/login/',LoginView.as_view()), path('auth/refresh/',TokenRefreshView.as_view()), path('auth/me/',MeView.as_view()),
 path('tablet/student/',TabletStudentView.as_view()), path('tablet/check-ins/',TabletCheckInView.as_view()),
 path('students/',StudentListCreateView.as_view()), path('students/<uuid:pk>/',StudentDetailView.as_view()), path('students/<uuid:pk>/history/',StudentHistoryView.as_view()), path('students/<uuid:student_id>/guardians/',GuardianCreateView.as_view()), path('students/<uuid:student_id>/guardians/<uuid:guardian_id>/',GuardianDetailView.as_view()),
 path('enrollments/',EnrollmentListCreateView.as_view()), path('enrollments/<uuid:pk>/',EnrollmentDetailView.as_view()),
 path('classes/',ClassListCreateView.as_view()), path('classes/<uuid:pk>/',ClassDetailView.as_view()),
 path('users/',UserListCreateView.as_view()), path('users/<uuid:pk>/',UserDetailView.as_view()),
 path('arrivals/',ArrivalListCreateView.as_view()), path('arrivals/<uuid:pk>/correction/',ArrivalCorrectionView.as_view()),
 path('dashboard/',DashboardView.as_view()), path('notifications/',NotificationListView.as_view()), path('notifications/process-now/',NotificationProcessView.as_view()),
]
