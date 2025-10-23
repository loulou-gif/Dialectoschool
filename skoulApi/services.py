import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from .models import *

# Configuration du logger pour les emails
logger = logging.getLogger(__name__)

def serviceSendEmail(email_obj):
    """
    Service d'envoi d'email avec gestion d'erreur améliorée
    """
    try:
        logger.info(f"Tentative d'envoi d'email: {email_obj.subject} -> {email_obj.to_email}")
        
        # Vérifier que l'email de destination est valide
        if not email_obj.to_email:
            logger.error("Email de destination manquant")
            return False
            
        # Envoyer l'email
        result = send_mail(
            subject=email_obj.subject,
            message=email_obj.message,
            recipient_list=[email_obj.to_email],
            from_email=email_obj.from_email,
            fail_silently=False,
        )
        
        # Vérifier le résultat
        if result:
            logger.info(f"Email envoyé avec succès à {email_obj.to_email}")
            # Marquer l'email comme envoyé
            email_obj.sent_at = timezone.now()
            email_obj.save()
            return True
        else:
            logger.error(f"Échec de l'envoi de l'email à {email_obj.to_email}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
        logger.error(f"Détails de l'email: Sujet='{email_obj.subject}', Destinataire='{email_obj.to_email}', Expéditeur='{email_obj.from_email}'")
        print(f"Error sending email: {e}")  # Garder pour compatibilité
        return False


def send_welcome_email(user, plain_password):
    """
    Envoie un email de bienvenue avec les identifiants de connexion
    
    Args:
        user: Instance de CustomUser
        plain_password: Mot de passe en clair (avant hachage)
    
    Returns:
        bool: True si l'email est envoyé avec succès, False sinon
    """
    try:
        logger.info(f"Préparation de l'email de bienvenue pour {user.email}")
        
        # Vérifier que l'utilisateur a un email
        if not user.email:
            logger.warning(f"L'utilisateur {user.username} n'a pas d'email. Email de bienvenue non envoyé.")
            return False
        
        # Déterminer le nom complet de l'utilisateur
        user_name = f"{user.first_name} {user.last_name}".strip() or user.username
        
        # Déterminer le rôle en français
        role_map = {
            'admin': 'Administrateur',
            'teacher': 'Enseignant',
            'student': 'Étudiant'
        }
        role_display = role_map.get(user.role, user.role)
        
        # Préparer le contexte pour le template
        context = {
            'user_name': user_name,
            'username': user.username,
            'email': user.email,
            'password': plain_password,
            'role': role_display,
            'login_link': 'http://localhost:5500/login.html',  # À personnaliser selon votre frontend
        }
        
        # Rendre le template HTML
        html_content = render_to_string('email/welcome.html', context)
        
        # Créer le message texte brut (fallback)
        text_content = f"""
Bienvenue sur DialectosKoul !

Bonjour {user_name},

Nous sommes ravis de vous accueillir sur la plateforme DialectosKoul !

Votre compte a été créé avec succès. Voici vos informations de connexion :

👤 Nom d'utilisateur : {user.username}
📧 Email : {user.email}
🔑 Mot de passe : {plain_password}
👔 Rôle : {role_display}

⚠️ Important : Pour des raisons de sécurité, nous vous recommandons de changer votre mot de passe lors de votre première connexion.

Si vous avez des questions ou besoin d'aide, n'hésitez pas à nous contacter.

Cordialement,
L'équipe DialectosKoul
        """
        
        # Créer l'email avec contenu HTML et texte brut
        email = EmailMultiAlternatives(
            subject='Bienvenue sur DialectosKoul - Vos identifiants de connexion',
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email]
        )
        
        # Attacher la version HTML
        email.attach_alternative(html_content, "text/html")
        
        # Envoyer l'email
        result = email.send(fail_silently=False)
        
        if result:
            logger.info(f"Email de bienvenue envoyé avec succès à {user.email}")
            
            # Sauvegarder l'email dans la base de données pour traçabilité
            EmailSendModel.objects.create(
                subject='Bienvenue sur DialectosKoul - Vos identifiants de connexion',
                message=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to_email=user.email,
                criticality='normal',
                sent_at=timezone.now()
            )
            
            return True
        else:
            logger.error(f"Échec de l'envoi de l'email de bienvenue à {user.email}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de bienvenue: {str(e)}")
        logger.error(f"Utilisateur concerné: {user.username} ({user.email})")
        print(f"Error sending welcome email: {e}")
        return False


def send_teacher_class_assignment_email(teacher, classe, is_new_assignment=True):
    """
    Envoie un email au professeur lors de son assignation à une classe
    
    Args:
        teacher: Instance de CustomUser (professeur)
        classe: Instance de Classes
        is_new_assignment: bool, True si nouvelle assignation, False si réassignation
    
    Returns:
        bool: True si l'email est envoyé avec succès, False sinon
    """
    try:
        logger.info(f"Préparation de l'email d'assignation de classe pour le professeur {teacher.email}")
        
        # Vérifier que le professeur a un email
        if not teacher.email:
            logger.warning(f"Le professeur {teacher.username} n'a pas d'email.")
            return False
        
        # Déterminer le nom complet du professeur
        teacher_name = f"{teacher.first_name} {teacher.last_name}".strip() or teacher.username
        
        # Récupérer les étudiants de la classe
        from .models import AffectationStudents
        affectations = AffectationStudents.objects.filter(classroom=classe)
        students = []
        for aff in affectations:
            students.append({
                'name': f"{aff.student.first_name} {aff.student.last_name}".strip() or aff.student.username,
                'email': aff.student.email
            })
        
        # Déterminer le titre de l'action
        action_title = "Assignation à une classe" if is_new_assignment else "Nouvelle classe assignée"
        
        # Préparer le contexte pour le template
        context = {
            'teacher_name': teacher_name,
            'class_name': classe.name,
            'level_name': classe.level.name if classe.level else "Non défini",
            'student_count': len(students),
            'students': students,
            'created_date': classe.created_at.strftime("%d/%m/%Y") if classe.created_at else None,
            'is_new_assignment': is_new_assignment,
            'action_title': action_title,
            'dashboard_link': 'http://localhost:5500/teacher-dashboard.html',
        }
        
        # Rendre le template HTML
        html_content = render_to_string('email/teacher_class_assignment.html', context)
        
        # Créer le message texte brut (fallback)
        text_content = f"""
{action_title}

Bonjour {teacher_name},

{'Nous avons le plaisir de vous informer que vous avez été assigné(e) comme professeur de la classe suivante :' if is_new_assignment else 'Nous vous informons que vous êtes désormais le professeur de la classe suivante :'}

📚 Informations de la classe
📝 Nom de la classe : {classe.name}
📊 Niveau : {classe.level.name if classe.level else 'Non défini'}
👥 Nombre d'étudiants : {len(students)}

Si vous avez des questions ou besoin d'informations complémentaires, n'hésitez pas à nous contacter.

Cordialement,
L'équipe DialectosKoul
        """
        
        # Créer l'email avec contenu HTML et texte brut
        subject = f"{action_title} - {classe.name}"
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[teacher.email]
        )
        
        # Attacher la version HTML
        email.attach_alternative(html_content, "text/html")
        
        # Envoyer l'email
        result = email.send(fail_silently=False)
        
        if result:
            logger.info(f"Email d'assignation de classe envoyé avec succès à {teacher.email}")
            
            # Sauvegarder l'email dans la base de données
            EmailSendModel.objects.create(
                subject=subject,
                message=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to_email=teacher.email,
                criticality='normal',
                sent_at=timezone.now()
            )
            
            return True
        else:
            logger.error(f"Échec de l'envoi de l'email au professeur {teacher.email}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email d'assignation: {str(e)}")
        print(f"Error sending teacher assignment email: {e}")
        return False


def send_student_class_assignment_email(student, classe, is_new_assignment=True):
    """
    Envoie un email à l'étudiant lors de son affectation/réaffectation à une classe
    
    Args:
        student: Instance de CustomUser (étudiant)
        classe: Instance de Classes
        is_new_assignment: bool, True si nouvelle affectation, False si réaffectation
    
    Returns:
        bool: True si l'email est envoyé avec succès, False sinon
    """
    try:
        logger.info(f"Préparation de l'email d'affectation de classe pour l'étudiant {student.email}")
        
        # Vérifier que l'étudiant a un email
        if not student.email:
            logger.warning(f"L'étudiant {student.username} n'a pas d'email.")
            return False
        
        # Déterminer le nom complet de l'étudiant
        student_name = f"{student.first_name} {student.last_name}".strip() or student.username
        
        # Récupérer les cours de la classe
        from .models import CoursAffectation
        course_affectations = CoursAffectation.objects.filter(classroom=classe)
        courses = []
        for ca in course_affectations:
            courses.append({
                'name': ca.course.name,
                'description': ca.course.descriptions[:100] + '...' if ca.course.descriptions and len(ca.course.descriptions) > 100 else ca.course.descriptions
            })
        
        # Déterminer le titre de l'action
        action_title = "Inscription dans une nouvelle classe" if is_new_assignment else "Réaffectation de classe"
        
        # Nom du professeur
        teacher_name = None
        if classe.teacher:
            teacher_name = f"{classe.teacher.first_name} {classe.teacher.last_name}".strip() or classe.teacher.username
        
        # Préparer le contexte pour le template
        context = {
            'student_name': student_name,
            'class_name': classe.name,
            'level_name': classe.level.name if classe.level else "Non défini",
            'teacher_name': teacher_name,
            'created_date': timezone.now().strftime("%d/%m/%Y"),
            'courses': courses,
            'courses_count': len(courses),
            'is_new_assignment': is_new_assignment,
            'action_title': action_title,
            'dashboard_link': 'http://localhost:5500/student-dashboard.html',
        }
        
        # Rendre le template HTML
        html_content = render_to_string('email/student_class_assignment.html', context)
        
        # Créer le message texte brut (fallback)
        text_content = f"""
{action_title}

Bonjour {student_name},

{'Nous avons le plaisir de vous informer que vous avez été inscrit(e) dans la classe suivante :' if is_new_assignment else 'Nous vous informons que vous avez été réaffecté(e) dans la classe suivante :'}

📚 Votre classe
📝 Nom de la classe : {classe.name}
📊 Niveau : {classe.level.name if classe.level else 'Non défini'}
{'👨‍🏫 Professeur : ' + teacher_name if teacher_name else ''}

📖 Cours disponibles ({len(courses)})
{chr(10).join(['  - ' + course['name'] for course in courses]) if courses else 'Aucun cours disponible pour le moment.'}

💡 Conseil : Connectez-vous à votre espace étudiant pour accéder à vos cours, devoirs et ressources pédagogiques.

Bon apprentissage !
L'équipe DialectosKoul
        """
        
        # Créer l'email avec contenu HTML et texte brut
        subject = f"{action_title} - {classe.name}"
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[student.email]
        )
        
        # Attacher la version HTML
        email.attach_alternative(html_content, "text/html")
        
        # Envoyer l'email
        result = email.send(fail_silently=False)
        
        if result:
            logger.info(f"Email d'affectation de classe envoyé avec succès à {student.email}")
            
            # Sauvegarder l'email dans la base de données
            EmailSendModel.objects.create(
                subject=subject,
                message=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to_email=student.email,
                criticality='normal',
                sent_at=timezone.now()
            )
            
            return True
        else:
            logger.error(f"Échec de l'envoi de l'email à l'étudiant {student.email}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email d'affectation: {str(e)}")
        print(f"Error sending student assignment email: {e}")
        return False


def send_homework_assignment_email(homework):
    """
    Envoie un email aux étudiants ciblés lors de la création d'un devoir
    
    Args:
        homework: Instance de Homework
    
    Returns:
        bool: True si tous les emails sont envoyés avec succès, False sinon
    """
    try:
        logger.info(f"Préparation de l'envoi d'emails pour le devoir {homework.name}")
        
        # Déterminer les étudiants ciblés
        if homework.is_individual and homework.student:
            # Devoir individuel - cibler un seul étudiant
            target_students = [homework.student]
            logger.info(f"Devoir individuel pour l'étudiant {homework.student.username}")
        else:
            # Devoir de classe - cibler tous les étudiants de la classe
            from .models import AffectationStudents
            affectations = AffectationStudents.objects.filter(classroom=homework.classes)
            target_students = [aff.student for aff in affectations]
            logger.info(f"Devoir de classe pour {len(target_students)} étudiants")
        
        if not target_students:
            logger.warning(f"Aucun étudiant ciblé pour le devoir {homework.name}")
            return False
        
        success_count = 0
        fail_count = 0
        
        for student in target_students:
            
            # Vérifier que l'étudiant a un email
            if not student.email:
                logger.warning(f"L'étudiant {student.username} n'a pas d'email.")
                fail_count += 1
                continue
            
            # Déterminer le nom complet de l'étudiant
            student_name = f"{student.first_name} {student.last_name}".strip() or student.username
            
            # Générer le lien de redirection vers l'application
            app_redirect_url = f"http://localhost:5500/homework/{homework.id}/"
            
            # Préparer le contexte pour le template
            context = {
                'student_name': student_name,
                'homework_name': homework.name,
                'homework_description': homework.description,
                'course_name': homework.course.name if homework.course else "Non spécifié",
                'class_name': homework.classes.name,
                'level_name': homework.level.name if homework.level else "Non défini",
                'created_date': homework.created_at.strftime("%d/%m/%Y") if homework.created_at else None,
                'end_date': homework.end_date.strftime("%d/%m/%Y à %H:%M") if homework.end_date else None,
                'app_redirect_url': app_redirect_url,
                'is_individual': homework.is_individual,
                'homework_id': homework.id,
            }
            
            # Rendre le template HTML
            html_content = render_to_string('email/homework_assignment.html', context)
            
            # Créer le message texte brut (fallback)
            individual_text = " (Devoir individuel)" if homework.is_individual else ""
            end_date_text = f"\n⏰ Date limite : {homework.end_date.strftime('%d/%m/%Y à %H:%M')}" if homework.end_date else ""
            
            text_content = f"""
Nouveau devoir à rendre{individual_text} !

Bonjour {student_name},

Un nouveau devoir vous a été attribué dans votre classe {homework.classes.name}.

📚 Détails du devoir
📝 Titre : {homework.name}
📖 Cours : {homework.course.name if homework.course else 'Non spécifié'}
🏫 Classe : {homework.classes.name}
📊 Niveau : {homework.level.name if homework.level else 'Non défini'}
📅 Date de création : {homework.created_at.strftime('%d/%m/%Y') if homework.created_at else None}{end_date_text}

📋 Description
{homework.description}

🔗 Accéder au devoir : {app_redirect_url}

💡 Important : Vous devez accéder au devoir via l'application DialectosKoul pour des raisons de sécurité.

Bon courage !
L'équipe DialectosKoul
            """
            
            # Créer l'email avec contenu HTML et texte brut
            subject = f"Nouveau devoir : {homework.name}"
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[student.email]
            )
            
            # Attacher la version HTML
            email.attach_alternative(html_content, "text/html")
            
            # Envoyer l'email
            result = email.send(fail_silently=False)
            
            if result:
                logger.info(f"Email de devoir envoyé avec succès à {student.email}")
                
                # Sauvegarder l'email dans la base de données
                EmailSendModel.objects.create(
                    subject=subject,
                    message=text_content,
                    from_email=settings.EMAIL_HOST_USER,
                    to_email=student.email,
                    criticality='normal',
                    sent_at=timezone.now()
                )
                
                success_count += 1
            else:
                logger.error(f"Échec de l'envoi de l'email à l'étudiant {student.email}")
                fail_count += 1
        
        logger.info(f"Emails de devoir envoyés : {success_count} succès, {fail_count} échecs")
        return success_count > 0
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi des emails de devoir: {str(e)}")
        print(f"Error sending homework assignment emails: {e}")
        return False


def send_homework_end_notification_email(homework):
    """
    Envoie un email aux étudiants quand un devoir arrive à sa date de dépublication
    
    Args:
        homework: Instance de Homework
    
    Returns:
        bool: True si tous les emails sont envoyés avec succès, False sinon
    """
    try:
        logger.info(f"Envoi de notifications de dépublication pour le devoir: {homework.name}")
        
        # Déterminer les étudiants ciblés
        if homework.is_individual and homework.student:
            target_students = [homework.student]
            logger.info(f"Notification de dépublication pour l'étudiant {homework.student.username}")
        else:
            from .models import AffectationStudents
            affectations = AffectationStudents.objects.filter(classroom=homework.classes)
            target_students = [aff.student for aff in affectations]
            logger.info(f"Notification de dépublication pour {len(target_students)} étudiants")
        
        if not target_students:
            logger.warning(f"Aucun étudiant ciblé pour la notification de dépublication du devoir {homework.name}")
            return False
        
        success_count = 0
        fail_count = 0
        
        for student in target_students:
            # Vérifier que l'étudiant a un email
            if not student.email:
                logger.warning(f"L'étudiant {student.username} n'a pas d'email.")
                fail_count += 1
                continue
            
            # Déterminer le nom complet de l'étudiant
            student_name = f"{student.first_name} {student.last_name}".strip() or student.username
            
            # Préparer le contexte pour le template
            context = {
                'student_name': student_name,
                'homework_name': homework.name,
                'homework_description': homework.description,
                'course_name': homework.course.name if homework.course else "Non spécifié",
                'class_name': homework.classes.name,
                'level_name': homework.level.name if homework.level else "Non défini",
                'end_date': homework.end_date.strftime("%d/%m/%Y à %H:%M") if homework.end_date else None,
                'is_individual': homework.is_individual,
                'homework_id': homework.id,
            }
            
            # Créer le message texte
            individual_text = " (Devoir individuel)" if homework.is_individual else ""
            
            text_content = f"""
Fin de disponibilité du devoir{individual_text}

Bonjour {student_name},

Le devoir "{homework.name}" n'est plus disponible depuis le {homework.end_date.strftime('%d/%m/%Y à %H:%M')}.

📚 Détails du devoir
📝 Titre : {homework.name}
📖 Cours : {homework.course.name if homework.course else 'Non spécifié'}
🏫 Classe : {homework.classes.name}
📊 Niveau : {homework.level.name if homework.level else 'Non défini'}
⏰ Date de fin : {homework.end_date.strftime('%d/%m/%Y à %H:%M')}

📋 Description
{homework.description}

ℹ️ Ce devoir n'est plus accessible. Si vous n'avez pas eu le temps de le terminer et que vous avez une raison valable (maladie, problème technique, etc.), veuillez contacter votre professeur.

Cordialement,
L'équipe DialectosKoul
            """
            
            # Créer l'email
            subject = f"Fin de disponibilité : {homework.name}"
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to=[student.email]
            )
            
            # Envoyer l'email
            result = email.send(fail_silently=False)
            
            if result:
                logger.info(f"Email de dépublication envoyé avec succès à {student.email}")
                
                # Sauvegarder l'email dans la base de données
                EmailSendModel.objects.create(
                    subject=subject,
                    message=text_content,
                    from_email=settings.EMAIL_HOST_USER,
                    to_email=student.email,
                    criticality='normal',
                    sent_at=timezone.now()
                )
                
                success_count += 1
            else:
                logger.error(f"Échec de l'envoi de l'email de dépublication à {student.email}")
                fail_count += 1
        
        logger.info(f"Notifications de dépublication envoyées : {success_count} succès, {fail_count} échecs")
        return success_count > 0
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi des notifications de dépublication: {str(e)}")
        return False


def send_homework_result_email(result_homework):
    """
    Envoie un email à l'étudiant lors de la saisie/mise à jour d'une note
    
    Args:
        result_homework: Instance de ResultHomework
    
    Returns:
        bool: True si l'email est envoyé avec succès, False sinon
    """
    try:
        # Vérifier que result_homework et student existent
        if not result_homework or not result_homework.student:
            logger.error("ResultHomework ou étudiant manquant")
            return False
        
        student = result_homework.student
        
        logger.info(f"Préparation de l'email de notification de note pour {student.email}")
        
        # Vérifier que l'étudiant a un email
        if not student.email:
            logger.warning(f"L'étudiant {student.username} n'a pas d'email.")
            return False
        
        # Déterminer le nom complet de l'étudiant
        first_name = student.first_name or ""
        last_name = student.last_name or ""
        student_name = f"{first_name} {last_name}".strip() or student.username
        
        # Déterminer la couleur et le message selon la note
        result = result_homework.result
        if result >= 16:
            color = '#10b981'  # Vert
            message = "Excellent travail ! Continuez sur cette lancée."
            performance = "Excellent"
        elif result >= 14:
            color = '#3b82f6'  # Bleu
            message = "Très bon travail ! Continuez vos efforts."
            performance = "Très bon"
        elif result >= 10:
            color = '#f59e0b'  # Orange
            message = "Bon travail. Vous pouvez encore vous améliorer."
            performance = "Bon"
        else:
            color = '#ef4444'  # Rouge
            message = "Vous pouvez mieux faire. N'hésitez pas à demander de l'aide."
            performance = "À améliorer"
        
        # Préparer le contexte pour le template
        # Gérer les cas où les champs peuvent être None
        homework_name = "Devoir"
        if result_homework.homework:
            homework_name = result_homework.homework.name or "Devoir"
        
        course_name = "Non spécifié"
        if result_homework.homework and result_homework.homework.course:
            course_name = result_homework.homework.course.name or "Non spécifié"
        
        class_name = "Non défini"
        if result_homework.class_name:
            class_name = result_homework.class_name.name or "Non défini"
        
        observation_text = result_homework.observation if result_homework.observation else "Aucune observation"
        
        context = {
            'student_name': student_name,
            'homework_name': homework_name,
            'course_name': course_name,
            'class_name': class_name,
            'result': result,
            'observation': observation_text,
            'created_date': result_homework.created_at.strftime("%d/%m/%Y") if result_homework.created_at else None,
            'color': color,
            'message': message,
            'performance': performance,
            'dashboard_link': 'http://localhost:5500/student-dashboard.html',
        }
        
        # Créer le message texte brut (pas de template HTML car il n'existe pas encore)
        text_content = f"""
Nouvelle note : {homework_name} - {result}/20

Bonjour {student_name},

Votre devoir a été corrigé et noté par votre professeur.

📚 Informations du devoir
📝 Titre : {homework_name}
📖 Cours : {course_name}
🏫 Classe : {class_name}
📅 Date de correction : {context['created_date']}

📊 Votre note : {result}/20
Performance : {performance}

💬 Observations du professeur
{observation_text}

💡 {message}

Continuez vos efforts !
L'équipe DialectosKoul
        """
        
        # Créer l'email
        subject = f"Nouvelle note : {homework_name} - {result}/20"
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[student.email]
        )
        
        # Envoyer l'email
        result_send = email.send(fail_silently=False)
        
        if result_send:
            logger.info(f"Email de note envoyé avec succès à {student.email}")
            
            # Sauvegarder l'email dans la base de données
            EmailSendModel.objects.create(
                subject=subject,
                message=text_content,
                from_email=settings.EMAIL_HOST_USER,
                to_email=student.email,
                criticality='normal',
                sent_at=timezone.now()
            )
            
            return True
        else:
            logger.error(f"Échec de l'envoi de l'email à l'étudiant {student.email}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de note: {str(e)}")
        print(f"Error sending homework result email: {e}")
        return False