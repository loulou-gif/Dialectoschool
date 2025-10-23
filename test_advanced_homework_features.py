#!/usr/bin/env python
"""
Script de test pour les nouvelles fonctionnalités avancées des devoirs
- Devoirs individuels (étudiant malade)
- Dates de fin de disponibilité
- Redirection sécurisée vers l'application
"""
import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dialectoskoul.settings')
django.setup()

from skoulApi.models import Homework, Courses, Classes, LevelClass, CustomUser, AffectationStudents
from skoulApi.tasks import send_scheduled_homeworks

def test_individual_homework():
    """
    Test des devoirs individuels
    """
    print("=== Test des devoirs individuels ===\n")
    
    try:
        # Récupérer des données de test
        level = LevelClass.objects.first()
        classe = Classes.objects.first()
        course = Courses.objects.first()
        
        # Récupérer un étudiant
        student = CustomUser.objects.filter(role='student').first()
        if not student:
            print("❌ Aucun étudiant trouvé. Veuillez créer des données de test.")
            return
        
        print(f"✅ Données de test trouvées:")
        print(f"   - Étudiant: {student.username}")
        print(f"   - Classe: {classe.name}")
        print(f"   - Cours: {course.name}")
        
        # Créer un devoir individuel
        homework = Homework.objects.create(
            name="Devoir de rattrapage - Mathématiques",
            description="Devoir individuel pour étudiant malade",
            form_link="https://forms.google.com/individual-test",
            course=course,
            classes=classe,
            level=level,
            student=student,
            is_individual=True,
            end_date=timezone.now() + timedelta(days=7)  # Disponible pendant 7 jours
        )
        
        print(f"\n✅ Devoir individuel créé:")
        print(f"   - ID: {homework.id}")
        print(f"   - Nom: {homework.name}")
        print(f"   - Étudiant ciblé: {homework.student.username}")
        print(f"   - Est individuel: {homework.is_individual}")
        print(f"   - Date de fin: {homework.end_date}")
        print(f"   - Est disponible: {homework.is_available}")
        print(f"   - Nombre d'étudiants ciblés: {len(homework.target_students)}")
        
        return homework
        
    except Exception as e:
        print(f"❌ Erreur lors du test des devoirs individuels: {e}")
        return None

def test_homework_with_end_date():
    """
    Test des devoirs avec date de fin
    """
    print("\n=== Test des devoirs avec date de fin ===\n")
    
    try:
        # Récupérer des données de test
        level = LevelClass.objects.first()
        classe = Classes.objects.first()
        course = Courses.objects.first()
        
        # Créer un devoir avec date de fin
        end_time = timezone.now() + timedelta(hours=2)  # Expire dans 2 heures
        
        homework = Homework.objects.create(
            name="Devoir avec limite de temps",
            description="Ce devoir expire dans 2 heures",
            form_link="https://forms.google.com/time-limited",
            course=course,
            classes=classe,
            level=level,
            end_date=end_time
        )
        
        print(f"✅ Devoir avec date de fin créé:")
        print(f"   - ID: {homework.id}")
        print(f"   - Nom: {homework.name}")
        print(f"   - Date de fin: {homework.end_date}")
        print(f"   - Est disponible: {homework.is_available}")
        
        # Créer un devoir expiré
        expired_time = timezone.now() - timedelta(hours=1)  # Expiré il y a 1 heure
        
        expired_homework = Homework.objects.create(
            name="Devoir expiré",
            description="Ce devoir a expiré",
            form_link="https://forms.google.com/expired",
            course=course,
            classes=classe,
            level=level,
            end_date=expired_time
        )
        
        print(f"\n✅ Devoir expiré créé:")
        print(f"   - ID: {expired_homework.id}")
        print(f"   - Nom: {expired_homework.name}")
        print(f"   - Date de fin: {expired_homework.end_date}")
        print(f"   - Est disponible: {expired_homework.is_available}")
        
        return homework, expired_homework
        
    except Exception as e:
        print(f"❌ Erreur lors du test des dates de fin: {e}")
        return None, None

def test_scheduled_individual_homework():
    """
    Test de la planification d'un devoir individuel
    """
    print("\n=== Test de planification de devoir individuel ===\n")
    
    try:
        # Récupérer des données de test
        level = LevelClass.objects.first()
        classe = Classes.objects.first()
        course = Courses.objects.first()
        student = CustomUser.objects.filter(role='student').first()
        
        if not student:
            print("❌ Aucun étudiant trouvé.")
            return
        
        # Créer un devoir individuel planifié
        scheduled_time = timezone.now() + timedelta(minutes=1)
        
        homework = Homework.objects.create(
            name="Devoir individuel planifié",
            description="Devoir planifié pour un étudiant spécifique",
            form_link="https://forms.google.com/scheduled-individual",
            course=course,
            classes=classe,
            level=level,
            student=student,
            is_individual=True,
            scheduled_date=scheduled_time,
            is_scheduled=True,
            is_sent=False
        )
        
        print(f"✅ Devoir individuel planifié créé:")
        print(f"   - ID: {homework.id}")
        print(f"   - Nom: {homework.name}")
        print(f"   - Étudiant: {homework.student.username}")
        print(f"   - Date planifiée: {homework.scheduled_date}")
        print(f"   - Est planifié: {homework.is_scheduled}")
        print(f"   - Est envoyé: {homework.is_sent}")
        
        return homework
        
    except Exception as e:
        print(f"❌ Erreur lors du test de planification: {e}")
        return None

def test_homework_statistics():
    """
    Test des statistiques des devoirs
    """
    print("\n=== Statistiques des devoirs ===\n")
    
    try:
        # Statistiques générales
        total_homeworks = Homework.objects.count()
        individual_homeworks = Homework.objects.filter(is_individual=True).count()
        scheduled_homeworks = Homework.objects.filter(is_scheduled=True, is_sent=False).count()
        sent_homeworks = Homework.objects.filter(is_sent=True).count()
        
        # Devoirs avec date de fin
        from django.utils import timezone
        from django.db.models import Q
        now = timezone.now()
        homeworks_with_end_date = Homework.objects.filter(end_date__isnull=False).count()
        available_homeworks = Homework.objects.filter(
            Q(end_date__isnull=True) | Q(end_date__gt=now)
        ).count()
        expired_homeworks = Homework.objects.filter(
            end_date__isnull=False,
            end_date__lte=now
        ).count()
        
        print(f"📊 Statistiques des devoirs:")
        print(f"   - Total des devoirs: {total_homeworks}")
        print(f"   - Devoirs individuels: {individual_homeworks}")
        print(f"   - Devoirs planifiés (non envoyés): {scheduled_homeworks}")
        print(f"   - Devoirs envoyés: {sent_homeworks}")
        print(f"   - Devoirs avec date de fin: {homeworks_with_end_date}")
        print(f"   - Devoirs disponibles: {available_homeworks}")
        print(f"   - Devoirs expirés: {expired_homeworks}")
        
    except Exception as e:
        print(f"❌ Erreur lors du calcul des statistiques: {e}")

def test_celery_task():
    """
    Test de la tâche Celery avec les nouvelles fonctionnalités
    """
    print("\n=== Test de la tâche Celery ===\n")
    
    try:
        print("🔄 Exécution de la tâche Celery...")
        result = send_scheduled_homeworks()
        print(f"✅ Résultat de la tâche: {result}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de la tâche: {e}")

def cleanup_test_data():
    """
    Nettoyer les données de test
    """
    print("\n🧹 Nettoyage des données de test...")
    
    try:
        # Supprimer les devoirs de test
        test_homeworks = Homework.objects.filter(
            name__startswith="Devoir de rattrapage"
        ) | Homework.objects.filter(
            name__startswith="Devoir avec limite"
        ) | Homework.objects.filter(
            name__startswith="Devoir expiré"
        ) | Homework.objects.filter(
            name__startswith="Devoir individuel planifié"
        )
        
        count = test_homeworks.count()
        test_homeworks.delete()
        print(f"✅ {count} devoirs de test supprimés")
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")

def main():
    """
    Fonction principale de test
    """
    print("🚀 Test des fonctionnalités avancées des devoirs\n")
    
    # Tests
    individual_hw = test_individual_homework()
    available_hw, expired_hw = test_homework_with_end_date()
    scheduled_hw = test_scheduled_individual_homework()
    
    # Statistiques
    test_homework_statistics()
    
    # Test Celery
    test_celery_task()
    
    print("\n=== Résumé des tests ===")
    if individual_hw:
        print(f"✅ Devoir individuel créé (ID: {individual_hw.id})")
    if available_hw:
        print(f"✅ Devoir avec date de fin créé (ID: {available_hw.id})")
    if expired_hw:
        print(f"✅ Devoir expiré créé (ID: {expired_hw.id})")
    if scheduled_hw:
        print(f"✅ Devoir individuel planifié créé (ID: {scheduled_hw.id})")
    
    # Demander si l'utilisateur veut nettoyer les données de test
    response = input("\nVoulez-vous nettoyer les données de test ? (y/N): ")
    if response.lower() in ['y', 'yes', 'oui']:
        cleanup_test_data()

if __name__ == "__main__":
    main()
