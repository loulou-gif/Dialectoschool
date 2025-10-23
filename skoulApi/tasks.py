from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Homework, AffectationStudents, EmailSendModel
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_scheduled_homeworks():
    """
    Tâche Celery pour envoyer les devoirs planifiés
    Cette tâche est exécutée périodiquement par Celery Beat
    """
    try:
        # Récupérer tous les devoirs planifiés qui n'ont pas encore été envoyés
        # et dont la date d'envoi est arrivée
        now = timezone.now()
        scheduled_homeworks = Homework.objects.filter(
            is_scheduled=True,
            is_sent=False,
            scheduled_date__lte=now
        )
        
        logger.info(f"Traitement de {scheduled_homeworks.count()} devoirs planifiés")
        
        for homework in scheduled_homeworks:
            try:
                # Envoyer le devoir aux étudiants
                success = send_homework_assignment_email_task(homework)
                
                if success:
                    # Marquer le devoir comme envoyé
                    homework.is_sent = True
                    homework.save()
                    logger.info(f"Devoir '{homework.name}' envoyé avec succès")
                else:
                    logger.error(f"Échec de l'envoi du devoir '{homework.name}'")
                    
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du devoir '{homework.name}': {str(e)}")
        
        return f"Traitement terminé: {scheduled_homeworks.count()} devoirs traités"
        
    except Exception as e:
        logger.error(f"Erreur dans la tâche send_scheduled_homeworks: {str(e)}")
        return f"Erreur: {str(e)}"

def send_homework_assignment_email_task(homework):
    """
    Envoie un email à tous les étudiants de la classe pour un devoir planifié
    
    Args:
        homework: Instance de Homework
    
    Returns:
        bool: True si tous les emails sont envoyés avec succès, False sinon
    """
    try:
        logger.info(f"Envoi d'emails pour le devoir planifié: {homework.name}")
        
        # Déterminer les étudiants ciblés
        if homework.is_individual and homework.student:
            # Devoir individuel - cibler un seul étudiant
            target_students = [homework.student]
        else:
            # Devoir de classe - cibler tous les étudiants de la classe
            affectations = AffectationStudents.objects.filter(classroom=homework.classes)
            target_students = [aff.student for aff in affectations]
        
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
                'scheduled_date': homework.scheduled_date.strftime("%d/%m/%Y à %H:%M") if homework.scheduled_date else None,
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
            scheduled_text = f"\n⏰ Envoyé le : {homework.scheduled_date.strftime('%d/%m/%Y à %H:%M')}" if homework.scheduled_date else ""
            
            text_content = f"""
Nouveau devoir à rendre{individual_text} !

Bonjour {student_name},

Un nouveau devoir vous a été attribué dans votre classe {homework.classes.name}.

📚 Détails du devoir
📝 Titre : {homework.name}
📖 Cours : {homework.course.name if homework.course else 'Non spécifié'}
🏫 Classe : {homework.classes.name}
📊 Niveau : {homework.level.name if homework.level else 'Non défini'}
📅 Date de création : {homework.created_at.strftime('%d/%m/%Y') if homework.created_at else None}{scheduled_text}{end_date_text}

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
                logger.info(f"Email de devoir planifié envoyé avec succès à {student.email}")
                
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
        
        logger.info(f"Emails de devoir planifié envoyés : {success_count} succès, {fail_count} échecs")
        return success_count > 0
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi des emails de devoir planifié: {str(e)}")
        return False

@shared_task
def send_homework_end_notifications():
    """
    Tâche Celery pour envoyer les notifications de dépublication des devoirs
    Cette tâche est exécutée périodiquement par Celery Beat
    """
    try:
        # Récupérer tous les devoirs qui ont atteint leur date de fin
        # et pour lesquels la notification n'a pas encore été envoyée
        now = timezone.now()
        ended_homeworks = Homework.objects.filter(
            end_date__isnull=False,
            end_date__lte=now,
            end_notification_sent=False
        )
        
        logger.info(f"Traitement de {ended_homeworks.count()} notifications de dépublication")
        
        for homework in ended_homeworks:
            try:
                # Envoyer les notifications aux étudiants
                from skoulApi.services import send_homework_end_notification_email
                success = send_homework_end_notification_email(homework)
                
                if success:
                    # Marquer la notification comme envoyée
                    homework.end_notification_sent = True
                    homework.save()
                    logger.info(f"Notification de dépublication envoyée pour '{homework.name}'")
                else:
                    logger.error(f"Échec de l'envoi de la notification de dépublication pour '{homework.name}'")
                    
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de la notification de dépublication pour '{homework.name}': {str(e)}")
        
        return f"Traitement terminé: {ended_homeworks.count()} notifications de dépublication traitées"
        
    except Exception as e:
        logger.error(f"Erreur dans la tâche send_homework_end_notifications: {str(e)}")
        return f"Erreur: {str(e)}"


@shared_task
def send_homework_reminder(homework_id):
    """
    Tâche pour envoyer un rappel de devoir (optionnel)
    """
    try:
        homework = Homework.objects.get(id=homework_id)
        # Logique pour envoyer un rappel
        logger.info(f"Rappel envoyé pour le devoir: {homework.name}")
        return f"Rappel envoyé pour le devoir: {homework.name}"
    except Homework.DoesNotExist:
        logger.error(f"Devoir avec l'ID {homework_id} non trouvé")
        return f"Devoir avec l'ID {homework_id} non trouvé"
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du rappel: {str(e)}")
        return f"Erreur: {str(e)}"
