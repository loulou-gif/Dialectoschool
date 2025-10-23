#!/usr/bin/env python
"""
Script de diagnostic pour vérifier pourquoi Celery n'envoie pas les emails
"""
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dialectoskoul.settings')
django.setup()

from skoulApi.models import Homework, CustomUser, AffectationStudents
from django.conf import settings

def check_redis():
    """Vérifier si Redis est accessible"""
    print("=== Vérification Redis ===\n")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis est accessible")
        return True
    except Exception as e:
        print(f"❌ Redis n'est pas accessible: {e}")
        print("\n💡 Solution: Démarrer Redis avec la commande:")
        print("   redis-server")
        return False

def check_celery_config():
    """Vérifier la configuration Celery"""
    print("\n=== Vérification Configuration Celery ===\n")
    try:
        print(f"CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
        print(f"CELERY_RESULT_BACKEND: {settings.CELERY_RESULT_BACKEND}")
        print(f"CELERY_TIMEZONE: {settings.CELERY_TIMEZONE}")
        print("✅ Configuration Celery trouvée")
        return True
    except AttributeError as e:
        print(f"❌ Configuration Celery manquante: {e}")
        return False

def check_email_config():
    """Vérifier la configuration email"""
    print("\n=== Vérification Configuration Email ===\n")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print("✅ Configuration email OK")

def check_scheduled_homeworks():
    """Vérifier les devoirs planifiés"""
    print("\n=== Vérification Devoirs Planifiés ===\n")
    now = timezone.now()
    
    # Devoirs planifiés à envoyer
    to_send = Homework.objects.filter(
        is_scheduled=True,
        is_sent=False,
        scheduled_date__lte=now
    )
    
    print(f"Devoirs planifiés à envoyer: {to_send.count()}")
    for hw in to_send:
        print(f"  - ID: {hw.id}, Nom: {hw.name}")
        print(f"    Date planifiée: {hw.scheduled_date}")
        print(f"    Classe: {hw.classes.name}")
        
        # Vérifier les étudiants
        if hw.is_individual:
            print(f"    Type: Individuel - {hw.student.username if hw.student else 'N/A'}")
        else:
            affectations = AffectationStudents.objects.filter(classroom=hw.classes)
            print(f"    Type: Classe - {affectations.count()} étudiants")
            for aff in affectations:
                print(f"      • {aff.student.username} ({aff.student.email})")
    
    # Devoirs planifiés futurs
    future = Homework.objects.filter(
        is_scheduled=True,
        is_sent=False,
        scheduled_date__gt=now
    )
    print(f"\nDevoirs planifiés futurs: {future.count()}")
    for hw in future:
        print(f"  - {hw.name} → {hw.scheduled_date}")
    
    # Devoirs déjà envoyés
    sent = Homework.objects.filter(is_sent=True)
    print(f"\nDevoirs déjà envoyés: {sent.count()}")

def check_end_notifications():
    """Vérifier les notifications de dépublication"""
    print("\n=== Vérification Notifications de Dépublication ===\n")
    now = timezone.now()
    
    # Devoirs expirés non notifiés
    to_notify = Homework.objects.filter(
        end_date__isnull=False,
        end_date__lte=now,
        end_notification_sent=False
    )
    
    print(f"Devoirs expirés à notifier: {to_notify.count()}")
    for hw in to_notify:
        print(f"  - ID: {hw.id}, Nom: {hw.name}")
        print(f"    Date de fin: {hw.end_date}")
        print(f"    Classe: {hw.classes.name}")
    
    # Devoirs avec notification envoyée
    notified = Homework.objects.filter(end_notification_sent=True)
    print(f"\nNotifications déjà envoyées: {notified.count()}")

def test_celery_task():
    """Tester l'exécution manuelle d'une tâche Celery"""
    print("\n=== Test Exécution Manuelle Tâches Celery ===\n")
    
    try:
        from skoulApi.tasks import send_scheduled_homeworks, send_homework_end_notifications
        
        print("🔄 Test: send_scheduled_homeworks()...")
        result1 = send_scheduled_homeworks()
        print(f"   Résultat: {result1}")
        
        print("\n🔄 Test: send_homework_end_notifications()...")
        result2 = send_homework_end_notifications()
        print(f"   Résultat: {result2}")
        
        print("\n✅ Les tâches s'exécutent manuellement")
        print("⚠️ Mais Celery Worker/Beat doit tourner pour l'automatisation")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des tâches: {e}")
        import traceback
        traceback.print_exc()

def check_celery_running():
    """Vérifier si Celery tourne"""
    print("\n=== Vérification Celery Worker/Beat ===\n")
    print("⚠️ Cette vérification ne peut pas être faite depuis Python")
    print("\n💡 Pour vérifier si Celery tourne:")
    print("   1. Ouvrez un autre terminal")
    print("   2. Exécutez: celery -A dialectoskoul inspect active")
    print("   3. Si erreur: Celery ne tourne pas")
    print("\n💡 Pour démarrer Celery:")
    print("   Terminal 1 - Worker:")
    print("   cd dialectoskoul")
    print("   celery -A dialectoskoul worker --loglevel=info")
    print("\n   Terminal 2 - Beat:")
    print("   cd dialectoskoul")
    print("   celery -A dialectoskoul beat --loglevel=info")

def create_test_homework():
    """Créer un devoir de test"""
    print("\n=== Création Devoir de Test ===\n")
    
    response = input("Voulez-vous créer un devoir de test planifié ? (y/N): ")
    if response.lower() not in ['y', 'yes', 'oui']:
        return
    
    try:
        from skoulApi.models import Courses, Classes, LevelClass
        
        level = LevelClass.objects.first()
        classe = Classes.objects.first()
        course = Courses.objects.first()
        
        if not all([level, classe, course]):
            print("❌ Données manquantes (niveau/classe/cours)")
            return
        
        # Créer un devoir planifié pour maintenant
        homework = Homework.objects.create(
            name="TEST - Devoir Planifié Automatique",
            description="Test d'envoi automatique par Celery",
            form_link="https://forms.google.com/test",
            course=course,
            classes=classe,
            level=level,
            scheduled_date=timezone.now() - timedelta(minutes=1),  # Il y a 1 minute
            is_scheduled=True,
            is_sent=False
        )
        
        print(f"✅ Devoir de test créé - ID: {homework.id}")
        print(f"   Date planifiée: {homework.scheduled_date}")
        print(f"   Ce devoir devrait être envoyé par Celery dans les 2 prochaines minutes")
        print(f"   (si Celery Worker et Beat tournent)")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale de diagnostic"""
    print("🔍 DIAGNOSTIC SYSTÈME D'ENVOI D'EMAILS\n")
    print("=" * 60)
    
    # Vérifications
    redis_ok = check_redis()
    celery_config_ok = check_celery_config()
    check_email_config()
    check_scheduled_homeworks()
    check_end_notifications()
    check_celery_running()
    
    # Tests
    if redis_ok and celery_config_ok:
        test_celery_task()
    
    # Création de test
    create_test_homework()
    
    # Résumé
    print("\n" + "=" * 60)
    print("\n📋 RÉSUMÉ DU DIAGNOSTIC\n")
    
    if not redis_ok:
        print("❌ PROBLÈME PRINCIPAL: Redis ne tourne pas")
        print("   Solution: redis-server")
    elif not celery_config_ok:
        print("❌ PROBLÈME: Configuration Celery incomplète")
    else:
        print("✅ Configuration OK")
        print("⚠️ Vérifiez que Celery Worker et Beat tournent:")
        print("   - celery -A dialectoskoul worker --loglevel=info")
        print("   - celery -A dialectoskoul beat --loglevel=info")
    
    print("\n💡 NEXT STEPS:")
    print("1. Démarrer Redis (si pas déjà fait)")
    print("2. Démarrer Celery Worker dans un terminal")
    print("3. Démarrer Celery Beat dans un autre terminal")
    print("4. Vérifier les logs dans les terminaux Celery")
    print("5. Les emails seront envoyés automatiquement")

if __name__ == "__main__":
    main()

