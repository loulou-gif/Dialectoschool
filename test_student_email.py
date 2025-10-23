#!/usr/bin/env python
"""
Script de test pour l'envoi d'email aux étudiants lors de l'affectation
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dialectoskoul.settings')
django.setup()

from skoulApi.models import CustomUser, Classes, LevelClass, AffectationStudents, Courses, CoursAffectation
from skoulApi.services import send_student_class_assignment_email

def test_student_affectation_email():
    """
    Test de l'envoi d'email lors de l'affectation d'un étudiant
    """
    print("\n" + "=" * 60)
    print("TEST : EMAIL D'AFFECTATION D'ÉTUDIANT")
    print("=" * 60)
    
    # Demander l'email de test
    test_email = input("Entrez l'email de l'étudiant pour le test: ").strip()
    if not test_email:
        print("❌ Email requis pour le test")
        return False
    
    try:
        # Créer un étudiant de test
        student = CustomUser.objects.create(
            username="student_test_demo",
            email=test_email,
            first_name="Étudiant",
            last_name="Test",
            role="student"
        )
        student.set_password("password123")
        student.save()
        print(f"✅ Étudiant de test créé: {student.username}")
        
        # Créer un professeur
        teacher = CustomUser.objects.create(
            username="prof_for_student_test",
            email="prof@test.com",
            first_name="Professeur",
            last_name="Test",
            role="teacher"
        )
        teacher.set_password("password123")
        teacher.save()
        print(f"✅ Professeur créé: {teacher.username}")
        
        # Créer un niveau
        level, _ = LevelClass.objects.get_or_create(name="Test Niveau Étudiant")
        print(f"✅ Niveau créé/récupéré: {level.name}")
        
        # Créer une classe
        classe = Classes.objects.create(
            name="Classe Test Email Étudiant",
            teacher=teacher,
            level=level
        )
        print(f"✅ Classe créée: {classe.name}")
        
        # Créer quelques cours
        course1 = Courses.objects.create(
            name="Mathématiques",
            level=level,
            descriptions="Cours de mathématiques pour le test"
        )
        course2 = Courses.objects.create(
            name="Français",
            level=level,
            descriptions="Cours de français pour le test"
        )
        print(f"✅ Cours créés: {course1.name}, {course2.name}")
        
        # Affecter les cours à la classe
        CoursAffectation.objects.create(course=course1, classroom=classe)
        CoursAffectation.objects.create(course=course2, classroom=classe)
        print(f"✅ Cours affectés à la classe")
        
        # Envoyer l'email d'affectation
        print(f"\n🔧 Envoi de l'email d'affectation à l'étudiant...")
        result = send_student_class_assignment_email(student, classe, is_new_assignment=True)
        
        if result:
            print("✅ Email d'affectation envoyé avec succès à l'étudiant!")
            print("   Vérifiez votre boîte de réception (et les spams)")
            print(f"\n📧 L'email contient:")
            print(f"   - Nom de la classe: {classe.name}")
            print(f"   - Niveau: {level.name}")
            print(f"   - Professeur: {teacher.first_name} {teacher.last_name}")
            print(f"   - Nombre de cours: 2")
            print(f"   - Liste des cours disponibles")
            
            # Test de réaffectation
            print(f"\n🔄 Test de réaffectation...")
            
            # Créer une nouvelle classe
            classe2 = Classes.objects.create(
                name="Classe Test Email Étudiant 2",
                teacher=teacher,
                level=level
            )
            print(f"✅ Nouvelle classe créée: {classe2.name}")
            
            # Envoyer l'email de réaffectation
            result2 = send_student_class_assignment_email(student, classe2, is_new_assignment=False)
            
            if result2:
                print("✅ Email de réaffectation envoyé avec succès!")
            else:
                print("❌ Échec de l'envoi de l'email de réaffectation")
            
            # Nettoyer
            response = input("\nNettoyer les données de test ? (o/N): ").strip().lower()
            if response == 'o':
                # Supprimer les objets créés
                CoursAffectation.objects.filter(classroom__in=[classe, classe2]).delete()
                classe.delete()
                classe2.delete()
                course1.delete()
                course2.delete()
                student.delete()
                teacher.delete()
                level.delete()
                print("✅ Données de test nettoyées")
            else:
                print("⚠️  Données de test conservées")
            
            return True
        else:
            print("❌ Échec de l'envoi de l'email d'affectation")
            
            # Nettoyer
            CoursAffectation.objects.filter(classroom=classe).delete()
            classe.delete()
            course1.delete()
            course2.delete()
            student.delete()
            teacher.delete()
            level.delete()
            
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST D'ENVOI D'EMAIL AUX ÉTUDIANTS")
    print("=" * 60)
    
    success = test_student_affectation_email()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 TEST RÉUSSI!")
        print("Le système d'email pour les étudiants fonctionne correctement.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ TEST ÉCHOUÉ")
        print("Vérifiez les logs dans email_logs.log")
        print("=" * 60)

