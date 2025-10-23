#!/usr/bin/env python
"""
Script de test pour le système de planification des devoirs
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

def test_homework_scheduling():
    """
    Test du système de planification des devoirs
    """
    print("=== Test du système de planification des devoirs ===\n")
    
    # 1. Vérifier qu'il y a des données de test
    try:
        # Récupérer un niveau, une classe et un cours existants
        level = LevelClass.objects.first()
        if not level:
            print("❌ Aucun niveau trouvé. Veuillez créer des données de test.")
            return
        
        classe = Classes.objects.first()
        if not classe:
            print("❌ Aucune classe trouvée. Veuillez créer des données de test.")
            return
            
        course = Courses.objects.first()
        if not course:
            print("❌ Aucun cours trouvé. Veuillez créer des données de test.")
            return
        
        print(f"✅ Données de test trouvées:")
        print(f"   - Niveau: {level.name}")
        print(f"   - Classe: {classe.name}")
        print(f"   - Cours: {course.name}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données: {e}")
        return
    
    # 2. Créer un devoir planifié
    try:
        # Planifier un devoir pour dans 1 minute
        scheduled_time = timezone.now() + timedelta(minutes=1)
        
        homework = Homework.objects.create(
            name="Test Devoir Planifié",
            description="Ceci est un devoir de test pour vérifier la planification",
            form_link="https://forms.google.com/test",
            course=course,
            classes=classe,
            level=level,
            scheduled_date=scheduled_time,
            is_scheduled=True,
            is_sent=False
        )
        
        print(f"\n✅ Devoir planifié créé:")
        print(f"   - ID: {homework.id}")
        print(f"   - Nom: {homework.name}")
        print(f"   - Date planifiée: {homework.scheduled_date}")
        print(f"   - Est planifié: {homework.is_scheduled}")
        print(f"   - Est envoyé: {homework.is_sent}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du devoir: {e}")
        return
    
    # 3. Créer un devoir planifié pour maintenant (pour test immédiat)
    try:
        homework_now = Homework.objects.create(
            name="Test Devoir Immédiat",
            description="Ceci est un devoir de test pour vérifier l'envoi immédiat",
            form_link="https://forms.google.com/test-now",
            course=course,
            classes=classe,
            level=level,
            scheduled_date=timezone.now() - timedelta(minutes=1),  # Dans le passé
            is_scheduled=True,
            is_sent=False
        )
        
        print(f"\n✅ Devoir pour test immédiat créé:")
        print(f"   - ID: {homework_now.id}")
        print(f"   - Nom: {homework_now.name}")
        print(f"   - Date planifiée: {homework_now.scheduled_date}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du devoir immédiat: {e}")
        return
    
    # 4. Tester la tâche Celery
    try:
        print(f"\n🔄 Exécution de la tâche Celery...")
        result = send_scheduled_homeworks()
        print(f"✅ Résultat de la tâche: {result}")
        
        # Vérifier l'état des devoirs après exécution
        homework_now.refresh_from_db()
        print(f"\n📊 État du devoir immédiat après exécution:")
        print(f"   - Est envoyé: {homework_now.is_sent}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de la tâche: {e}")
    
    # 5. Afficher les statistiques
    try:
        total_homeworks = Homework.objects.count()
        scheduled_homeworks = Homework.objects.filter(is_scheduled=True, is_sent=False).count()
        sent_homeworks = Homework.objects.filter(is_sent=True).count()
        
        print(f"\n📈 Statistiques des devoirs:")
        print(f"   - Total des devoirs: {total_homeworks}")
        print(f"   - Devoirs planifiés (non envoyés): {scheduled_homeworks}")
        print(f"   - Devoirs envoyés: {sent_homeworks}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des statistiques: {e}")
    
    print(f"\n=== Fin du test ===")

def cleanup_test_data():
    """
    Nettoyer les données de test
    """
    print("\n🧹 Nettoyage des données de test...")
    
    try:
        # Supprimer les devoirs de test
        test_homeworks = Homework.objects.filter(
            name__startswith="Test Devoir"
        )
        count = test_homeworks.count()
        test_homeworks.delete()
        print(f"✅ {count} devoirs de test supprimés")
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")

if __name__ == "__main__":
    test_homework_scheduling()
    
    # Demander si l'utilisateur veut nettoyer les données de test
    response = input("\nVoulez-vous nettoyer les données de test ? (y/N): ")
    if response.lower() in ['y', 'yes', 'oui']:
        cleanup_test_data()
