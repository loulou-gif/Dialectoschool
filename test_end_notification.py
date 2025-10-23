#!/usr/bin/env python
"""
Script de test pour les notifications de dépublication des devoirs
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
from skoulApi.tasks import send_homework_end_notifications
from skoulApi.services import send_homework_end_notification_email

def test_end_notification():
    """
    Test complet du système de notifications de dépublication
    """
    print("=== Test des notifications de dépublication ===\n")
    
    try:
        # 1. Récupérer les données de test
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
        
        # 2. Créer un devoir expiré (date de fin dans le passé)
        past_time = timezone.now() - timedelta(minutes=5)
        
        homework_expired = Homework.objects.create(
            name="Test Devoir Expiré",
            description="Ce devoir a expiré il y a 5 minutes",
            form_link="https://forms.google.com/test-expired",
            course=course,
            classes=classe,
            level=level,
            end_date=past_time,
            end_notification_sent=False
        )
        
        print(f"\n✅ Devoir expiré créé:")
        print(f"   - ID: {homework_expired.id}")
        print(f"   - Date de fin: {homework_expired.end_date}")
        print(f"   - Est disponible: {homework_expired.is_available}")
        print(f"   - Notification envoyée: {homework_expired.end_notification_sent}")
        
        # 3. Créer un devoir individuel expiré
        homework_individual_expired = Homework.objects.create(
            name="Test Devoir Individuel Expiré",
            description="Devoir individuel expiré",
            form_link="https://forms.google.com/test-individual-expired",
            course=course,
            classes=classe,
            level=level,
            student=student,
            is_individual=True,
            end_date=past_time,
            end_notification_sent=False
        )
        
        print(f"\n✅ Devoir individuel expiré créé:")
        print(f"   - ID: {homework_individual_expired.id}")
        print(f"   - Étudiant: {homework_individual_expired.student.username}")
        print(f"   - Date de fin: {homework_individual_expired.end_date}")
        
        # 4. Créer un devoir qui va expirer (pas encore expiré)
        future_time = timezone.now() + timedelta(hours=1)
        
        homework_future = Homework.objects.create(
            name="Test Devoir Futur",
            description="Ce devoir expire dans 1 heure",
            form_link="https://forms.google.com/test-future",
            course=course,
            classes=classe,
            level=level,
            end_date=future_time,
            end_notification_sent=False
        )
        
        print(f"\n✅ Devoir futur créé:")
        print(f"   - ID: {homework_future.id}")
        print(f"   - Date de fin: {homework_future.end_date}")
        print(f"   - Est disponible: {homework_future.is_available}")
        
        # 5. Tester l'envoi direct
        print(f"\n🔄 Test d'envoi direct avec send_homework_end_notification_email...")
        success = send_homework_end_notification_email(homework_expired)
        print(f"   Résultat: {'✅ Succès' if success else '❌ Échec'}")
        
        # 6. Marquer manuellement comme envoyé pour éviter doublon
        homework_expired.end_notification_sent = True
        homework_expired.save()
        
        # 7. Exécuter la tâche Celery
        print(f"\n🔄 Exécution de la tâche Celery send_homework_end_notifications...")
        result = send_homework_end_notifications()
        print(f"   Résultat: {result}")
        
        # 8. Vérifier l'état après exécution
        homework_individual_expired.refresh_from_db()
        homework_future.refresh_from_db()
        
        print(f"\n📊 État après exécution de la tâche Celery:")
        print(f"   - Devoir individuel notification envoyée: {homework_individual_expired.end_notification_sent}")
        print(f"   - Devoir futur notification envoyée: {homework_future.end_notification_sent} (devrait être False)")
        
        # 9. Statistiques
        total_expired = Homework.objects.filter(
            end_date__isnull=False,
            end_date__lte=timezone.now()
        ).count()
        
        total_notified = Homework.objects.filter(
            end_notification_sent=True
        ).count()
        
        print(f"\n📈 Statistiques:")
        print(f"   - Total devoirs expirés: {total_expired}")
        print(f"   - Total notifications envoyées: {total_notified}")
        
        # 10. Vérifier les logs
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

if __name__ == "__main__":
    test_end_notification()

