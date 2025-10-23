"""
URL configuration for dialectoskoul project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from skoulApi.views import *
from rest_framework.authtoken.views import obtain_auth_token
from . import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'users', UserViews, basename='users')
router.register(r'user', UserViewSet, basename='user')
router.register(r'user-info', UserDetailViewSet, basename='user-info')
router.register(r'classes', ClassesViewSet, basename='classes')
router.register(r'level', LevelClassViewSet, basename='levels')
router.register(r'affectationStudents', AffectationStudentViewSet, basename='AffectatioStudent')
router.register(r'diffusionList', DiffusionListViewSet, basename='diffusionList')
router.register(r'APILogEntry', APILogEntryViewSet, basename='APILogEntry')
router.register(r'sendEmail', EmailViewSet, basename="sendEmail")
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'courses-affectation', CourseAffectationViewSet, basename='courses_affectation')
router.register(r'homework', HomeworkViewSet, basename='homework')
router.register(r'result-homework', ResultHomeworkViewSet, basename='result-homework')

urlpatterns = [
    path('admin/', admin.site.urls),  # Interface d'administration Django
    path('api/', include(router.urls)),  # Inclure les URLs générées par Django REST Framework
    # path('api/api-auth/', include('rest_framework.urls')),  # Temporairement désactivé
    path('api/dj_rest_auth/', include('dj_rest_auth.urls')),
    path('api/teachers/', get_teachers, name='get_teachers'),
    path('api/students/', get_students, name='get_students'),
    path('api/levels/', get_levels, name='get_levels'),
    path('api/roles/', get_roles, name='get_roles'),
    # Nouvelles APIs pour les informations étudiantes
    path('api/student/info/', get_student_info, name='get_student_info'),
    path('api/student/info/<int:student_id>/', get_student_info, name='get_student_info_by_id'),
    path('api/student/average/<int:student_id>/', get_student_average, name='get_student_average'),
    # Nouvelles APIs pour les utilisateurs par ID
    path('api/user-details/<int:user_id>/', get_user_details, name='get_user_details'),
    path('api/user-complete-info/<int:user_id>/', get_user_complete_info, name='get_user_complete_info'),
    # Nouvelles APIs pour les emails utilisateur
    path('api/my-emails/', get_my_emails, name='get_my_emails'),
    path('api/user-emails/<int:user_id>/', get_user_emails, name='get_user_emails'),
    path('api/user-emails/', get_user_emails_by_email, name='get_user_emails_by_email'),
    # Nouvelles APIs pour les imports en masse
    path('api/bulk-create-users/', bulk_create_users_from_excel, name='bulk_create_users'),
    path('api/bulk-assign-students/', bulk_assign_students_to_class, name='bulk_assign_students'),
    # API pour déclencher l'envoi des devoirs planifiés
    path('api/send-homework-notifications/', send_homework_notifications, name='send_homework_notifications'),
    # path('api/token/', obtain_auth_token, name='api_token_auth'),
]+ static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)
