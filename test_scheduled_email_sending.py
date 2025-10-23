#!/usr/bin/env python
"""
Script de test pour vérifier l'envoi d'emails pour les devoirs programmés
"""
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dialectoskoul.settings')
django.setup()

from skoulApi.models import Homework, Courses, Classes, LevelClass, CustomUser
from skoulApi.tasks import send_scheduled_homeworks
from skoulApi.services import send_homework_assignment_email

def test_scheduled_homework_email():
    """
    Test complet de l'envoi d'emails pour devoirs programmés
    """
    print("=== Test d'envoi d'emails pour devoirs programmés ===\n")
    
    try:
        # 1. Vérifier qu'il y a des données
        level = LevelClass.objects.first()
        classe = Classes.objects.first()
        course = Courses.objects.first()
        student = CustomUser.objects.filter(role='student').first()
        
        if not all([level, classe, course, student]):
            print("❌ Données de test manquantes")
            return
        
        print(f"✅ Données trouvées:")
        print(f"   - Niveau: {level.name}")
        print(f"   - Classe: {classe.name}")
        print(f"   - Cours: {course.name}")
        print(f"   - Étudiant: {student.username} ({student.email})")
        
        # 2. Créer un devoir programmé dans le passé (devrait être envoyé)
        past_time = timezone.now() - timedelta(minutes=5)
        
        homework_past = Homework.objects.create(
            name="Test Devoir Programmé (Passé)",
            description="Ce devoir devrait être envoyé immédiatement",
            form_link="https://forms.google.com/test-past",
            course=course,
            classes=classe,
            level=level,
            scheduled_date=past_time,
            is_scheduled=True,
            is_sent=False
        )
        
        print(f"\n✅ Devoir programmé créé (date passée):")
        print(f"   - ID: {homework_past.id}")
        print(f"   - Date programmée: {homework_past.scheduled_date}")
        print(f"   - Est envoyé: {homework_past.is_sent}")
        
        # 3. Créer un devoir individuel programmé dans le passé
        homework_individual = Homework.objects.create(
            name="Test Devoir Individuel Programmé",
            description="Devoir individuel pour étudiant spécifique",
            form_link="https://forms.google.com/test-individual",
            course=course,
            classes=classe,
            level=level,
            student=student,
            is_individual=True,
            scheduled_date=past_time,
            is_scheduled=True,
            is_sent=False
        )
        
        print(f"\n✅ Devoir individuel programmé créé:")
        print(f"   - ID: {homework_individual.id}")
        print(f"   - Étudiant: {homework_individual.student.username}")
        print(f"   - Date programmée: {homework_individual.scheduled_date}")
        
        # 4. Tester l'envoi direct
        print(f"\n🔄 Test d'envoi direct avec send_homework_assignment_email...")
        
        test_homework = Homework.objects.create(
            name="Test Envoi Direct",
            description="Test d'envoi direct",
            form_link="https://forms.google.com/test-direct",
            course=course,
            classes=classe,
            level=level,
            scheduled_date=None,
            is_scheduled=False,
            is_sent=False
        )
        
        success = send_homework_assignment_email(test_homework)
        print(f"   Résultat: {'✅ Succès' if success else '❌ Échec'}")
        
        # 5. Exécuter la tâche Celery
        print(f"\n🔄 Exécution de la tâche Celery send_scheduled_homeworks...")
        result = send_scheduled_homeworks()
        print(f"   Résultat: {result}")
        
        # 6. Vérifier l'état après exécution
        homework_past.refresh_from_db()
        homework_individual.refresh_from_db()
        
        print(f"\n📊 État après exécution de la tâche Celery:")
        print(f"   - Devoir de classe envoyé: {homework_past.is_sent}")
        print(f"   - Devoir individuel envoyé: {homework_individual.is_sent}")
        
        # 7. Statistiques
        total_scheduled = Homework.objects.filter(is_scheduled=True, is_sent=False).count()
        total_sent = Homework.objects.filter(is_sent=True).count()
        
        print(f"\n📈 Statistiques:")
        print(f"   - Devoirs programmés non envoyés: {total_scheduled}")
        print(f"   - Total devoirs envoyés: {total_sent}")
        
        # 8. Vérifier les logs
        print(f"\n💡 Vérifiez les logs d'email dans: email_logs.log")
        
        # Nettoyage
        cleanup = input("\nVoulez-vous nettoyer les devoirs de test ? (y/N): ")
        if cleanup.lower() in ['y', 'yes', 'oui']:
            Homework.objects.filter(name__startswith="Test").delete()
            print("✅ Devoirs de test supprimés")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

def check_email_configuration():
    """
    Vérifier la configuration email
    """
    print("\n=== Vérification de la configuration email ===\n")
    
    from django.conf import settings
    
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

if __name__ == "__main__":
    check_email_configuration()
    test_scheduled_homework_email()

