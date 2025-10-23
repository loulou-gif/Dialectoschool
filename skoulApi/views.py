from unittest import expectedFailure
from django.db import models
from django.db.models import Q
from rest_framework import viewsets
from .models import CustomUser
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .services import serviceSendEmail
from .serializers import *
from .models import *
from rest_framework import status
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

# Create your models here.
class UserDetailViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]  # Ajout des permissions

    @action(detail=False, methods=['get'], url_path='details')
    def all_user_details(self, request):
        users = CustomUser.objects.all() 
        serializer = UserDetailsSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='details/(?P<user_id>[^/.]+)')
    def user_detail(self, request, user_id=None):
        """Récupère les détails d'un utilisateur spécifique"""
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = UserDetailsSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='complete-info/(?P<user_id>[^/.]+)')
    def user_complete_info(self, request, user_id=None):
        """Récupère les informations complètes d'un utilisateur spécifique"""
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = StudentCompleteInfoSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=False, methods=['get'], url_path='roles')
    def get_roles(self, request):
        roles = [{"value": r[0], "label": r[1]} for r in CustomUser.ROLE_CHOICES]
        return Response(roles)
    
    
class UserViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]  # Changé de IsAuthenticated à AllowAny

    @action(detail=False, methods=['get'], url_path='me/email')
    def get_email(self, request):
        user = request.user
        return Response({
            "email": user.email,
            "username": user.username,
            "id": user.id,
        })

    @action(detail=False, methods=['get'], url_path='me/complete-info')
    def get_complete_info(self, request):
        """Récupère toutes les informations de l'utilisateur connecté"""
        user = request.user
        
        # Retiré la vérification de rôle étudiant
        serializer = StudentCompleteInfoSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='me/profile')
    def get_profile(self, request):
        """Récupère le profil de base de l'utilisateur connecté"""
        user = request.user
        serializer = UserDetailsSerializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='details/(?P<user_id>[^/.]+)')
    def user_details(self, request, user_id=None):
        """Récupère les détails d'un utilisateur spécifique"""
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = UserDetailsSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='complete-info/(?P<user_id>[^/.]+)')
    def user_complete_info(self, request, user_id=None):
        """Récupère les informations complètes d'un utilisateur spécifique"""
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = StudentCompleteInfoSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

class UserViews(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Changé de IsAuthenticated à AllowAny
    
# class StudentsViews(viewsets.ModelViewSet):
#     # queryset = UserJoinRules.objects.filter(rules=UserJoinRules.rules)
#     serializer_class = UserJoinRuleSerializers
    
#     def get_queryset(self):
#         queryset = UserJoinRules.objects.all()
#         name_filter = self.request.query_params.get('students', None)
#         if name_filter:
#             queryset = queryset.filter(rules=name_filter)
#         return queryset
    
    
    
    
class LevelClassViewSet(viewsets.ModelViewSet):
    queryset = LevelClass.objects.all()
    serializer_class = LevelClassSerializer
    permission_classes = [AllowAny]  # Changé de IsAuthenticated à AllowAny

class APILogEntryViewSet(viewsets.ModelViewSet):
    queryset = APILogEntry.objects.all().order_by('-created_at')
    serializer_class = APILogEntrySerializer
    permission_classes = [AllowAny]  # Changé de IsAdminUser à AllowAny
    
class ClassesViewSet(viewsets.ModelViewSet):
    serializer_class = ClassesSerializer
    permission_classes = [AllowAny]  # Changé de IsAuthenticated à AllowAny

    def get_queryset(self):
        
        user = self.request.user
        
        queryset = Classes.objects.all()
            
        if user.role == 'teacher':
            queryset = Classes.objects.filter(teacher=user)
        elif user.role == 'admin':
            queryset = Classes.objects.all()
        elif user.role == 'student':
            try:
                affectation = AffectationStudents.objects.get(student=user)
                queryset = Classes.objects.filter(id=affectation.classroom.id)
            except AffectationStudents.DoesNotExist:
                queryset = Classes.objects.none()
        
        level_id = self.request.query_params.get('level')
        
        if level_id:
            queryset = queryset.filter(level_id=level_id)
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='my-class')
    def my_class(self):
        """Retourne uniquement la classe de l'utilisateur connecté"""
        user = self.request.user
        if user.role == "student":
            affectation = AffectationStudents.objects.filter(student=user).first()
            if affectation:
                serializer = self.get_serializer(affectation.classroom)
                return Response(serializer.data)
        return Response({"message": "Aucune classe trouvée."})

    
class AffectationStudentViewSet(viewsets.ModelViewSet): 
    queryset = AffectationStudents.objects.all()
    serializer_class = AffectationStudentSerializer
    permission_classes = [AllowAny]  # Changé de IsAuthenticated à AllowAny

    def perform_create(self, serializer):
        affectation = serializer.save()
        classe = affectation.classroom
        student = affectation.student
        
        try:
            diffusion = DiffusionList.objects.get(name=classe.name)
            diffusion.email.add(student)
        except DiffusionList.DoesNotExist:
            # Si jamais elle n'existe pas (bug, suppression...), on la recrée
            diffusion = DiffusionList.objects.create(name=classe.name)
            diffusion.email.add(student)

    
    
class DiffusionListViewSet(viewsets.ModelViewSet): 
    queryset = DiffusionList.objects.all()
    serializer_class = DiffusionListSerializer
    permission_classes = [AllowAny]  # Changé de IsAuthenticated à AllowAny

    

class EmailViewSet(viewsets.ModelViewSet):
    queryset = EmailSendModel.objects.all().order_by('-created_at')
    serializer_class = SendMailSerializer
    permission_classes = [AllowAny]  # Changé de IsAdminUser à AllowAny

    def perform_create(self, serializer):
        diffusion_list = self.request.data.get("diffusion_list")

        if diffusion_list:
            # On ne sauvegarde pas serializer.save() ici, car on va créer manuellement les emails
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']
            from_email = serializer.validated_data['from_email']
            criticality = serializer.validated_data['criticality']
            
            # On récupère la liste de diffusion complète via l'instance serializer
            diffusion = serializer.validated_data['diffusion_list']
            for user in diffusion.email.all():
                email_copy = EmailSendModel.objects.create(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    to_email=user.email,
                    criticality=criticality
                )
                serviceSendEmail(email_copy)
        else:
            # Cas normal : un seul destinataire
            email_obj = serializer.save()
            serviceSendEmail(email_obj)

    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        email_obj = self.get_object()
        success = serviceSendEmail(email_obj)

        if success:
            return Response({'message': 'Email envoyé avec succès'}, status=status.HTTP_200_OK)
        return Response({"Statut": "Échec de l'envoi de mail"}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def get_teachers(request):
    teachers = CustomUser.objects.filter(role='teacher')
    serializer = UserSerializer(teachers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_students(request):
    students = CustomUser.objects.filter(role='student')
    serializer = UserSerializer(students, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_levels(request):
    levels = LevelClass.objects.all()
    serializer = LevelClassSerializer(levels, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_roles(request):
    """API pour récupérer tous les rôles disponibles"""
    roles = [
        {
            "value": choice[0],
            "label": choice[1]
        }
        for choice in CustomUser.ROLE_CHOICES
    ]
    return Response(roles)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Courses.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]  # Changé de IsAuthenticated à AllowAny
    def get_queriset(self):
        user = self.request.user
        
        queryset = Courses.objects.all()
        
        if user.role == 'teacher':
            queryset = Courses.objects.all()
        elif user.role == 'admin':
            queryset = Courses.objects.all()
        elif user.role == 'student':
            try:
                affectation = AffectationStudents.objects.get(student=user)
                
                class_id = CoursAffectation.objects.get(classroom=affectation.classroom).values_list('course_id', flat=True)
                
                queryset = Courses.objects.filter(id__in=class_id)
            except AffectationStudents.DoesNotExist:
                queryset = Courses.objects.none()
        
        return queryset
    
class CourseAffectationViewSet(viewsets.ModelViewSet):
    queryset = CoursAffectation.objects.all()
    serializer_class = CourseAffectationSerializer
    permission_classes = [AllowAny]  # Changé de IsAuthenticated à AllowAny

@api_view(['GET'])
def get_student_info(request, student_id=None):
    """API pour récupérer les informations d'un étudiant spécifique (admin/professeur)"""
    # Retiré toutes les vérifications d'authentification et permissions
    
    # Si pas d'ID fourni, utiliser l'utilisateur connecté
    if student_id is None:
        student = request.user
    else:
        try:
            student = CustomUser.objects.get(id=student_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "Étudiant non trouvé"}, status=status.HTTP_404_NOT_FOUND)
    
    # Retiré la vérification de rôle étudiant
    serializer = StudentCompleteInfoSerializer(student)
    return Response(serializer.data)

@api_view(['GET'])
def get_student_average(request, student_id):
    """API pour récupérer uniquement la moyenne d'un étudiant"""
    # Retiré la vérification d'authentification
    
    try:
        student = CustomUser.objects.get(id=student_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "Étudiant non trouvé"}, status=status.HTTP_404_NOT_FOUND)
    
    # Retiré la vérification de rôle étudiant
    
    # Calculer la moyenne des devoirs
    results = ResultHomework.objects.filter(student=student)
    
    # Gérer le nom complet de l'étudiant
    first_name = student.first_name or ""
    last_name = student.last_name or ""
    student_name = f"{first_name} {last_name}".strip()
    if not student_name:
        student_name = student.username
    
    if not results:
        return Response({
            "student_id": student.id,
            "student_name": student_name,
            "average_score": 0,
            "total_tests": 0
        })
    
    total_score = 0
    for result in results:
        total_score += result.result
    
    average = round(total_score / len(results), 2)
    
    return Response({
        "student_id": student.id,
        "student_name": student_name,
        "average_score": average,
        "total_tests": len(results)
    })

@api_view(['GET'])
def get_user_details(request, user_id):
    """API pour récupérer les détails d'un utilisateur spécifique"""
    try:
        user = CustomUser.objects.get(id=user_id)
        serializer = UserDetailsSerializer(user)
        return Response(serializer.data)
    except CustomUser.DoesNotExist:
        return Response({"error": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_user_complete_info(request, user_id):
    """API pour récupérer les informations complètes d'un utilisateur spécifique"""
    try:
        user = CustomUser.objects.get(id=user_id)
        serializer = StudentCompleteInfoSerializer(user)
        return Response(serializer.data)
    except CustomUser.DoesNotExist:
        return Response({"error": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_user_emails(request, user_id):
    """API pour récupérer les emails destinés à un utilisateur spécifique"""
    try:
        user = CustomUser.objects.get(id=user_id)
        user_email = user.email
        
        # Récupérer les emails envoyés directement à cet utilisateur
        direct_emails = EmailSendModel.objects.filter(to_email=user_email)
        
        # Récupérer les emails envoyés aux listes de diffusion dont l'utilisateur fait partie
        user_diffusion_lists = DiffusionList.objects.filter(email=user)
        diffusion_emails = EmailSendModel.objects.filter(diffusion_list__in=user_diffusion_lists)
        
        # Combiner et dédupliquer les résultats
        all_emails = list(direct_emails) + list(diffusion_emails)
        unique_emails = list({email.id: email for email in all_emails}.values())
        
        # Trier par date d'envoi (plus récent en premier)
        unique_emails.sort(key=lambda x: x.sent_at, reverse=True)
        
        serializer = UserEmailSerializer(unique_emails, many=True)
        return Response(serializer.data)
        
    except CustomUser.DoesNotExist:
        return Response({"error": "Utilisateur non trouvé"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_user_emails_by_email(request):
    """API pour récupérer les emails destinés à un utilisateur par son email"""
    user_email = request.query_params.get('email')
    
    if not user_email:
        return Response({"error": "Paramètre 'email' requis"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = CustomUser.objects.get(email=user_email)
        return get_user_emails(request, user.id)
    except CustomUser.DoesNotExist:
        # Même si l'utilisateur n'existe pas, on peut chercher les emails envoyés à cet email
        # Récupérer les emails envoyés directement à cet email
        direct_emails = EmailSendModel.objects.filter(to_email=user_email)
        
        # Récupérer les emails envoyés aux listes de diffusion qui contiennent cet email
        user_diffusion_lists = DiffusionList.objects.filter(email__email=user_email)
        diffusion_emails = EmailSendModel.objects.filter(diffusion_list__in=user_diffusion_lists)
        
        # Combiner et dédupliquer les résultats
        all_emails = list(direct_emails) + list(diffusion_emails)
        unique_emails = list({email.id: email for email in all_emails}.values())
        
        # Trier par date d'envoi (plus récent en premier)
        unique_emails.sort(key=lambda x: x.sent_at, reverse=True)
        
        serializer = UserEmailSerializer(unique_emails, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def get_my_emails(request):
    """API pour récupérer les emails de l'utilisateur connecté"""
    user = request.user
    
    if not user.is_authenticated:
        return Response({"error": "Utilisateur non connecté"}, status=status.HTTP_401_UNAUTHORIZED)
    
    user_email = user.email
    
    # Récupérer les emails envoyés directement à cet utilisateur
    direct_emails = EmailSendModel.objects.filter(to_email=user_email)
    
    # Récupérer les emails envoyés aux listes de diffusion dont l'utilisateur fait partie
    user_diffusion_lists = DiffusionList.objects.filter(email=user)
    diffusion_emails = EmailSendModel.objects.filter(diffusion_list__in=user_diffusion_lists)
    
    # Combiner et dédupliquer les résultats
    all_emails = list(direct_emails) + list(diffusion_emails)
    unique_emails = list({email.id: email for email in all_emails}.values())
    
    # Trier par date d'envoi (plus récent en premier)
    unique_emails.sort(key=lambda x: x.sent_at, reverse=True)
    
    serializer = UserEmailSerializer(unique_emails, many=True)
    return Response(serializer.data)


class HomeworkViewSet(viewsets.ModelViewSet):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [AllowAny]  # Changé de IsAuthenticated à AllowAny
    
    def get_queryset(self):
        user = self.request.user
        queryset = Homework.objects.all()
        
        # Si l'utilisateur est authentifié, filtrer selon son rôle
        if user.is_authenticated and hasattr(user, 'role'):
            if user.role == 'teacher':
                queryset = Homework.objects.all()
            elif user.role == 'admin':
                queryset = Homework.objects.all()
            elif user.role == 'student':
                affectation = AffectationStudents.objects.filter(student=user).first()
                if affectation:
                    course_ids = CoursAffectation.objects.filter(classroom=affectation.classroom).values_list('course_id', flat=True)
                    queryset = Homework.objects.filter(course_id__in=course_ids)
                    
                    # Filtrer les devoirs expirés pour les étudiants
                    from django.utils import timezone
                    now = timezone.now()
                    queryset = queryset.filter(
                        Q(end_date__isnull=True) | Q(end_date__gt=now)
                    )
                else:
                    queryset = Homework.objects.none()

        # Optimisation : précharger les relations pour éviter N+1 queries
        queryset = queryset.select_related(
            'course', 'classes', 'level', 'student'
        ).prefetch_related(
            'classes__affectationstudents_set'
        ).order_by('-created_at')

        return queryset
    
    @action(detail=True, methods=['post'])
    def send_now(self, request, pk=None):
        """
        Action pour envoyer immédiatement un devoir planifié
        """
        homework = self.get_object()
        
        if homework.is_sent:
            return Response({
                'message': 'Ce devoir a déjà été envoyé aux étudiants',
                'status': 'already_sent'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Envoyer le devoir immédiatement
            from .services import send_homework_assignment_email
            success = send_homework_assignment_email(homework)
            
            if success:
                # Marquer comme envoyé
                homework.is_sent = True
                homework.is_scheduled = False  # Désactiver la planification
                homework.save()
                
                return Response({
                    'message': 'Devoir envoyé avec succès à tous les étudiants',
                    'status': 'sent'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'Erreur lors de l\'envoi du devoir',
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'message': f'Erreur lors de l\'envoi: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def cancel_schedule(self, request, pk=None):
        """
        Action pour annuler la planification d'un devoir
        """
        homework = self.get_object()
        
        if not homework.is_scheduled:
            return Response({
                'message': 'Ce devoir n\'est pas planifié',
                'status': 'not_scheduled'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Annuler la planification
        homework.is_scheduled = False
        homework.scheduled_date = None
        homework.save()
        
        return Response({
            'message': 'Planification du devoir annulée',
            'status': 'cancelled'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def scheduled(self, request):
        """
        Action pour récupérer tous les devoirs planifiés
        """
        scheduled_homeworks = Homework.objects.filter(
            is_scheduled=True,
            is_sent=False
        ).order_by('scheduled_date')
        
        serializer = self.get_serializer(scheduled_homeworks, many=True)
        return Response({
            'scheduled_homeworks': serializer.data,
            'count': scheduled_homeworks.count()
        })
    
    @action(detail=False, methods=['get'])
    def individual(self, request):
        """
        Action pour récupérer tous les devoirs individuels
        """
        individual_homeworks = Homework.objects.filter(
            is_individual=True
        ).order_by('-created_at')
        
        serializer = self.get_serializer(individual_homeworks, many=True)
        return Response({
            'individual_homeworks': serializer.data,
            'count': individual_homeworks.count()
        })
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Action pour récupérer tous les devoirs disponibles (non expirés)
        """
        from django.utils import timezone
        now = timezone.now()
        
        available_homeworks = Homework.objects.filter(
            Q(end_date__isnull=True) | Q(end_date__gt=now)
        ).order_by('-created_at')
        
        serializer = self.get_serializer(available_homeworks, many=True)
        return Response({
            'available_homeworks': serializer.data,
            'count': available_homeworks.count()
        })
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """
        Action pour récupérer tous les devoirs expirés
        """
        from django.utils import timezone
        now = timezone.now()
        
        expired_homeworks = Homework.objects.filter(
            end_date__isnull=False,
            end_date__lte=now
        ).order_by('-end_date')
        
        serializer = self.get_serializer(expired_homeworks, many=True)
        return Response({
            'expired_homeworks': serializer.data,
            'count': expired_homeworks.count()
        })
    
    @action(detail=True, methods=['get'])
    def access_form(self, request, pk=None):
        """
        Action pour accéder au formulaire d'un devoir (redirection sécurisée)
        """
        homework = self.get_object()
        
        # Vérifier si l'utilisateur a le droit d'accéder à ce devoir
        user = request.user
        
        if user.role == 'student':
            # Vérifier si l'étudiant est ciblé par ce devoir
            if homework.is_individual:
                if homework.student != user:
                    return Response({
                        'error': 'Vous n\'avez pas accès à ce devoir individuel'
                    }, status=status.HTTP_403_FORBIDDEN)
            else:
                # Vérifier si l'étudiant est dans la classe
                from .models import AffectationStudents
                try:
                    affectation = AffectationStudents.objects.get(student=user)
                    if affectation.classroom != homework.classes:
                        return Response({
                            'error': 'Vous n\'avez pas accès à ce devoir'
                        }, status=status.HTTP_403_FORBIDDEN)
                except AffectationStudents.DoesNotExist:
                    return Response({
                        'error': 'Vous n\'êtes pas affecté à une classe'
                    }, status=status.HTTP_403_FORBIDDEN)
        
        # Vérifier si le devoir est encore disponible
        if not homework.is_available:
            return Response({
                'error': 'Ce devoir n\'est plus disponible',
                'end_date': homework.end_date.strftime('%d/%m/%Y à %H:%M') if homework.end_date else None
            }, status=status.HTTP_410_GONE)
        
        # Retourner les informations du devoir et le lien du formulaire
        return Response({
            'homework': self.get_serializer(homework).data,
            'form_link': homework.form_link,
            'access_granted': True
        })
    

class ResultHomeworkViewSet(viewsets.ModelViewSet):
    queryset = ResultHomework.objects.all()
    serializer_class = ResultHomeworkSerializer
    permission_classes = [AllowAny]  # Changé de IsAuthenticated à AllowAny
    
    def get_queryset(self):
        user = self.request.user
        queryset = ResultHomework.objects.all()
        
        # Si l'utilisateur n'est pas authentifié, retourner tous les résultats
        if not user.is_authenticated:
            return queryset.select_related('student', 'homework', 'class_name').order_by('-created_at')
        
        if user.role == 'teacher' or user.role == "admin":
            # Teachers et admins voient tous les résultats
            return queryset.select_related('student', 'homework', 'class_name').order_by('-created_at')
            
        elif user.role == 'student':
            # Les étudiants ne voient que leurs propres résultats
            return queryset.filter(student=user).select_related('homework', 'class_name').order_by('-created_at')
        
        return queryset.select_related('student', 'homework', 'class_name').order_by('-created_at')
    
    @action(detail=False, methods=['get'], url_path='by-student/(?P<student_id>[^/.]+)')
    def by_student(self, request, student_id=None):
        """Récupérer tous les résultats d'un étudiant spécifique"""
        try:
            student = CustomUser.objects.get(id=student_id, role='student')
            results = ResultHomework.objects.filter(student=student).select_related('homework', 'class_name').order_by('-created_at')
            serializer = self.get_serializer(results, many=True)
            return Response({
                'student_id': student.id,
                'student_name': f"{student.first_name} {student.last_name}".strip() or student.username,
                'results': serializer.data,
                'total_results': results.count()
            })
        except CustomUser.DoesNotExist:
            return Response({"error": "Étudiant non trouvé"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='by-class/(?P<class_id>[^/.]+)')
    def by_class(self, request, class_id=None):
        """Récupérer tous les résultats d'une classe spécifique"""
        try:
            classe = Classes.objects.get(id=class_id)
            results = ResultHomework.objects.filter(class_name=classe).select_related('student', 'homework').order_by('-created_at')
            serializer = self.get_serializer(results, many=True)
            return Response({
                'class_id': classe.id,
                'class_name': classe.name,
                'results': serializer.data,
                'total_results': results.count()
            })
        except Classes.DoesNotExist:
            return Response({"error": "Classe non trouvée"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='by-homework/(?P<homework_id>[^/.]+)')
    def by_homework(self, request, homework_id=None):
        """Récupérer tous les résultats pour un devoir spécifique"""
        try:
            homework = Homework.objects.get(id=homework_id)
            results = ResultHomework.objects.filter(homework=homework).select_related('student', 'class_name').order_by('-created_at')
            serializer = self.get_serializer(results, many=True)
            return Response({
                'homework_id': homework.id,
                'homework_name': homework.name,
                'results': serializer.data,
                'total_results': results.count()
            })
        except Homework.DoesNotExist:
            return Response({"error": "Devoir non trouvé"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Récupérer des statistiques générales sur les résultats"""
        queryset = self.get_queryset()
        
        total_results = queryset.count()
        if total_results == 0:
            return Response({
                'total_results': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0
            })
        
        from django.db.models import Avg, Max, Min
        stats = queryset.aggregate(
            average=Avg('result'),
            highest=Max('result'),
            lowest=Min('result')
        )
        
        return Response({
            'total_results': total_results,
            'average_score': round(stats['average'], 2) if stats['average'] else 0,
            'highest_score': stats['highest'],
            'lowest_score': stats['lowest']
        }) 


# =====================================================================
# SERVICES D'IMPORT EN MASSE
# =====================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_create_users_from_excel(request):
    """
    Service d'import en masse d'utilisateurs depuis un fichier Excel
    
    Format attendu du fichier Excel :
    - Colonne 1: username
    - Colonne 2: email
    - Colonne 3: password
    - Colonne 4: first_name
    - Colonne 5: last_name
    - Colonne 6: role (student, teacher, admin)
    
    Exemple de requête :
    POST /api/bulk-create-users/
    Content-Type: multipart/form-data
    file: [fichier Excel]
    """
    import pandas as pd
    import io
    
    if 'file' not in request.FILES:
        return Response({
            "error": "Aucun fichier fourni",
            "message": "Veuillez fournir un fichier Excel avec le paramètre 'file'"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    
    # Vérifier l'extension du fichier
    if not file.name.endswith(('.xlsx', '.xls')):
        return Response({
            "error": "Format de fichier invalide",
            "message": "Le fichier doit être au format Excel (.xlsx ou .xls)"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(file)
        
        # Vérifier les colonnes requises
        required_columns = ['username', 'email', 'password', 'role']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return Response({
                "error": "Colonnes manquantes",
                "message": f"Les colonnes suivantes sont requises : {', '.join(missing_columns)}",
                "columns_found": list(df.columns)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Statistiques
        created_users = []
        failed_users = []
        updated_users = []
        
        # Parcourir les lignes du fichier
        for index, row in df.iterrows():
            try:
                # Récupérer les données de la ligne
                username = str(row.get('username', '')).strip()
                email = str(row.get('email', '')).strip()
                password = str(row.get('password', '')).strip()
                first_name = str(row.get('first_name', '')).strip() if pd.notna(row.get('first_name')) else ''
                last_name = str(row.get('last_name', '')).strip() if pd.notna(row.get('last_name')) else ''
                role = str(row.get('role', 'student')).strip().lower()
                
                # Validation basique
                if not username or not email or not password:
                    failed_users.append({
                        "row": index + 2,  # +2 pour compter l'en-tête et l'indexation à partir de 1
                        "username": username,
                        "error": "username, email et password sont obligatoires"
                    })
                    continue
                
                # Vérifier si le rôle est valide
                if role not in ['student', 'teacher', 'admin']:
                    role = 'student'  # Par défaut
                
                # Vérifier si l'utilisateur existe déjà
                existing_user = CustomUser.objects.filter(username=username).first()
                
                if existing_user:
                    # Mettre à jour l'utilisateur existant
                    existing_user.email = email
                    existing_user.first_name = first_name
                    existing_user.last_name = last_name
                    existing_user.role = role
                    existing_user.set_password(password)
                    existing_user.save()
                    
                    updated_users.append({
                        "row": index + 2,
                        "username": username,
                        "email": email,
                        "role": role
                    })
                else:
                    # Créer un nouvel utilisateur
                    user = CustomUser.objects.create(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        role=role
                    )
                    user.set_password(password)
                    user.save()
                    
                    # Envoyer l'email de bienvenue
                    try:
                        from skoulApi.services import send_welcome_email
                        send_welcome_email(user, password)
                    except Exception as e:
                        print(f"Erreur lors de l'envoi de l'email de bienvenue à {email}: {e}")
                    
                    created_users.append({
                        "row": index + 2,
                        "username": username,
                        "email": email,
                        "role": role
                    })
                    
            except Exception as e:
                failed_users.append({
                    "row": index + 2,
                    "username": row.get('username', 'N/A'),
                    "error": str(e)
                })
        
        # Préparer la réponse
        response_data = {
            "success": True,
            "message": "Import terminé",
            "statistics": {
                "total_rows": len(df),
                "created": len(created_users),
                "updated": len(updated_users),
                "failed": len(failed_users)
            },
            "created_users": created_users,
            "updated_users": updated_users,
            "failed_users": failed_users
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            "error": "Erreur lors de la lecture du fichier",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_homework_notifications(request):
    """
    ⚠️ ENDPOINT DÉSACTIVÉ pour des raisons de performance
    
    L'envoi des devoirs planifiés est maintenant géré automatiquement par Celery Beat
    (toutes les 60 secondes en arrière-plan).
    
    Pour l'activer, assurez-vous que Celery Beat tourne :
    celery -A dialectoskoul beat --loglevel=info
    
    Cet endpoint ne fait maintenant qu'afficher un statut.
    """
    try:
        from .models import Homework
        from django.utils import timezone
        
        now = timezone.now()
        scheduled_count = Homework.objects.filter(
            is_scheduled=True,
            is_sent=False,
            scheduled_date__lte=now
        ).count()
        
        return Response({
            'status': 'info',
            'message': 'Cet endpoint est désactivé. Celery Beat gère automatiquement les devoirs planifiés.',
            'scheduled_homeworks_pending': scheduled_count,
            'info': 'Celery Beat vérifie automatiquement toutes les 60 secondes.',
            'recommendation': 'Laissez Celery Beat gérer les devoirs planifiés automatiquement.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur lors de la consultation: {str(e)}")
        return Response({
            'error': f'Erreur: {str(e)}',
            'status': 'error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_assign_students_to_class(request):
    """
    Service d'affectation en masse d'étudiants à une classe
    
    Deux méthodes supportées :
    
    1. Par liste d'IDs (JSON) :
    {
        "class_id": 5,
        "student_ids": [1, 2, 3, 4, 5]
    }
    
    2. Par fichier Excel :
    - Colonne 1: student_id ou student_username ou student_email
    - Avec un paramètre class_id dans la requête
    
    Exemple de requête JSON :
    POST /api/bulk-assign-students/
    Content-Type: application/json
    {
        "class_id": 5,
        "student_ids": [1, 2, 3, 4, 5]
    }
    
    Exemple de requête avec fichier Excel :
    POST /api/bulk-assign-students/
    Content-Type: multipart/form-data
    class_id: 5
    file: [fichier Excel]
    """
    import pandas as pd
    
    # Vérifier si c'est une requête JSON ou avec fichier
    if request.content_type == 'application/json' or 'student_ids' in request.data:
        # Méthode 1 : Par liste d'IDs (JSON)
        class_id = request.data.get('class_id')
        student_ids = request.data.get('student_ids', [])
        
        if not class_id:
            return Response({
                "error": "class_id est requis"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not student_ids or not isinstance(student_ids, list):
            return Response({
                "error": "student_ids doit être une liste d'IDs"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier que la classe existe
        try:
            classe = Classes.objects.get(id=class_id)
        except Classes.DoesNotExist:
            return Response({
                "error": "Classe non trouvée",
                "class_id": class_id
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Statistiques
        assigned_students = []
        failed_students = []
        updated_students = []
        
        for student_id in student_ids:
            try:
                # Vérifier que l'étudiant existe
                try:
                    student = CustomUser.objects.get(id=student_id, role='student')
                except CustomUser.DoesNotExist:
                    failed_students.append({
                        "student_id": student_id,
                        "error": "Étudiant non trouvé ou n'est pas un étudiant"
                    })
                    continue
                
                # Vérifier si l'étudiant est déjà affecté à une classe
                existing_affectation = AffectationStudents.objects.filter(student=student).first()
                
                if existing_affectation:
                    # Mettre à jour l'affectation existante
                    old_class = existing_affectation.classroom.name
                    existing_affectation.classroom = classe
                    existing_affectation.save()
                    
                    # Envoyer un email de réaffectation
                    try:
                        from skoulApi.services import send_student_class_assignment_email
                        send_student_class_assignment_email(student, classe, is_new_assignment=False)
                    except Exception as e:
                        print(f"Erreur lors de l'envoi de l'email de réaffectation: {e}")
                    
                    updated_students.append({
                        "student_id": student.id,
                        "username": student.username,
                        "email": student.email,
                        "old_class": old_class,
                        "new_class": classe.name
                    })
                else:
                    # Créer une nouvelle affectation
                    affectation = AffectationStudents.objects.create(
                        student=student,
                        classroom=classe
                    )
                    
                    # Envoyer un email d'affectation
                    try:
                        from skoulApi.services import send_student_class_assignment_email
                        send_student_class_assignment_email(student, classe, is_new_assignment=True)
                    except Exception as e:
                        print(f"Erreur lors de l'envoi de l'email d'affectation: {e}")
                    
                    assigned_students.append({
                        "student_id": student.id,
                        "username": student.username,
                        "email": student.email,
                        "class": classe.name
                    })
                    
            except Exception as e:
                failed_students.append({
                    "student_id": student_id,
                    "error": str(e)
                })
        
        # Préparer la réponse
        response_data = {
            "success": True,
            "message": "Affectation en masse terminée",
            "class": {
                "id": classe.id,
                "name": classe.name,
                "level": classe.level.name if classe.level else None
            },
            "statistics": {
                "total_students": len(student_ids),
                "assigned": len(assigned_students),
                "updated": len(updated_students),
                "failed": len(failed_students)
            },
            "assigned_students": assigned_students,
            "updated_students": updated_students,
            "failed_students": failed_students
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    elif 'file' in request.FILES:
        # Méthode 2 : Par fichier Excel
        class_id = request.data.get('class_id')
        file = request.FILES['file']
        
        if not class_id:
            return Response({
                "error": "class_id est requis"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier l'extension du fichier
        if not file.name.endswith(('.xlsx', '.xls')):
            return Response({
                "error": "Format de fichier invalide",
                "message": "Le fichier doit être au format Excel (.xlsx ou .xls)"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier que la classe existe
        try:
            classe = Classes.objects.get(id=class_id)
        except Classes.DoesNotExist:
            return Response({
                "error": "Classe non trouvée",
                "class_id": class_id
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Lire le fichier Excel
            df = pd.read_excel(file)
            
            # Déterminer la colonne à utiliser pour identifier les étudiants
            identifier_column = None
            if 'student_id' in df.columns:
                identifier_column = 'student_id'
            elif 'student_username' in df.columns:
                identifier_column = 'student_username'
            elif 'student_email' in df.columns:
                identifier_column = 'student_email'
            else:
                return Response({
                    "error": "Colonne d'identification manquante",
                    "message": "Le fichier doit contenir au moins une des colonnes suivantes : student_id, student_username, student_email",
                    "columns_found": list(df.columns)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Statistiques
            assigned_students = []
            failed_students = []
            updated_students = []
            
            # Parcourir les lignes du fichier
            for index, row in df.iterrows():
                try:
                    identifier = row.get(identifier_column)
                    
                    if pd.isna(identifier):
                        failed_students.append({
                            "row": index + 2,
                            "error": f"{identifier_column} est vide"
                        })
                        continue
                    
                    # Chercher l'étudiant selon le type d'identifiant
                    student = None
                    if identifier_column == 'student_id':
                        try:
                            student = CustomUser.objects.get(id=int(identifier), role='student')
                        except (CustomUser.DoesNotExist, ValueError):
                            failed_students.append({
                                "row": index + 2,
                                "identifier": identifier,
                                "error": "Étudiant non trouvé avec cet ID"
                            })
                            continue
                    elif identifier_column == 'student_username':
                        try:
                            student = CustomUser.objects.get(username=str(identifier), role='student')
                        except CustomUser.DoesNotExist:
                            failed_students.append({
                                "row": index + 2,
                                "identifier": identifier,
                                "error": "Étudiant non trouvé avec ce username"
                            })
                            continue
                    elif identifier_column == 'student_email':
                        try:
                            student = CustomUser.objects.get(email=str(identifier), role='student')
                        except CustomUser.DoesNotExist:
                            failed_students.append({
                                "row": index + 2,
                                "identifier": identifier,
                                "error": "Étudiant non trouvé avec cet email"
                            })
                            continue
                    
                    if not student:
                        continue
                    
                    # Vérifier si l'étudiant est déjà affecté à une classe
                    existing_affectation = AffectationStudents.objects.filter(student=student).first()
                    
                    if existing_affectation:
                        # Mettre à jour l'affectation existante
                        old_class = existing_affectation.classroom.name
                        existing_affectation.classroom = classe
                        existing_affectation.save()
                        
                        # Envoyer un email de réaffectation
                        try:
                            from skoulApi.services import send_student_class_assignment_email
                            send_student_class_assignment_email(student, classe, is_new_assignment=False)
                        except Exception as e:
                            print(f"Erreur lors de l'envoi de l'email de réaffectation: {e}")
                        
                        updated_students.append({
                            "row": index + 2,
                            "student_id": student.id,
                            "username": student.username,
                            "email": student.email,
                            "old_class": old_class,
                            "new_class": classe.name
                        })
                    else:
                        # Créer une nouvelle affectation
                        affectation = AffectationStudents.objects.create(
                            student=student,
                            classroom=classe
                        )
                        
                        # Envoyer un email d'affectation
                        try:
                            from skoulApi.services import send_student_class_assignment_email
                            send_student_class_assignment_email(student, classe, is_new_assignment=True)
                        except Exception as e:
                            print(f"Erreur lors de l'envoi de l'email d'affectation: {e}")
                        
                        assigned_students.append({
                            "row": index + 2,
                            "student_id": student.id,
                            "username": student.username,
                            "email": student.email,
                            "class": classe.name
                        })
                        
                except Exception as e:
                    failed_students.append({
                        "row": index + 2,
                        "identifier": row.get(identifier_column, 'N/A'),
                        "error": str(e)
                    })
            
            # Préparer la réponse
            response_data = {
                "success": True,
                "message": "Affectation en masse terminée",
                "class": {
                    "id": classe.id,
                    "name": classe.name,
                    "level": classe.level.name if classe.level else None
                },
                "statistics": {
                    "total_rows": len(df),
                    "assigned": len(assigned_students),
                    "updated": len(updated_students),
                    "failed": len(failed_students)
                },
                "assigned_students": assigned_students,
                "updated_students": updated_students,
                "failed_students": failed_students
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "error": "Erreur lors de la lecture du fichier",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        return Response({
            "error": "Données invalides",
            "message": "Veuillez fournir soit 'student_ids' (JSON) soit un fichier Excel avec 'file'"
        }, status=status.HTTP_400_BAD_REQUEST)
            