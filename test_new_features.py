#!/usr/bin/env python
"""
Script de test pour les nouvelles fonctionnalités
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dialectoskoul.settings')
django.setup()

from skoulApi.models import CustomUser, Classes, LevelClass
from skoulApi.services import send_teacher_class_assignment_email
from django.db import IntegrityError

def test_email_uniqueness():
    """
    Test de l'unicité de l'email
    """
    print("\n" + "=" * 60)
    print("TEST 1 : UNICITÉ DE L'EMAIL")
    print("=" * 60)
    
    test_email = "test_unique@example.com"
    
    try:
        # Essayer de créer un premier utilisateur
        user1 = CustomUser.objects.create(
            username="test_user_1",
            email=test_email,
            first_name="Test",
            last_name="User1"
        )
        user1.set_password("password123")
        user1.save()
        print(f"✅ Premier utilisateur créé avec l'email: {test_email}")
        
        # Essayer de créer un deuxième utilisateur avec le même email
        try:
            user2 = CustomUser.objects.create(
                username="test_user_2",
                email=test_email,  # Même email !
                first_name="Test",
                last_name="User2"
            )
            user2.set_password("password123")
            user2.save()
            print("❌ ERREUR: Le deuxième utilisateur a été créé avec le même email !")
            
            # Nettoyer
            user1.delete()
            user2.delete()
            return False
            
        except IntegrityError as e:
            print(f"✅ Contrainte d'unicité respectée ! Le deuxième utilisateur n'a pas été créé.")
            print(f"   Message d'erreur: {str(e)[:100]}...")
            
            # Nettoyer
            user1.delete()
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_teacher_email():
    """
    Test de l'envoi d'email au professeur
    """
    print("\n" + "=" * 60)
    print("TEST 2 : EMAIL AU PROFESSEUR")
    print("=" * 60)
    
    # Demander l'email de test
    test_email = input("Entrez l'email du professeur pour le test (ou appuyez sur Entrée pour skip): ").strip()
    if not test_email:
        print("⏭️  Test skippé")
        return True
    
    try:
        # Créer un professeur de test
        teacher = CustomUser.objects.create(
            username="prof_test_demo",
            email=test_email,
            first_name="Professeur",
            last_name="Test",
            role="teacher"
        )
        teacher.set_password("password123")
        teacher.save()
        print(f"✅ Professeur de test créé: {teacher.username}")
        
        # Créer un niveau
        level, created = LevelClass.objects.get_or_create(name="Test Niveau")
        print(f"✅ Niveau créé/récupéré: {level.name}")
        
        # Créer une classe
        classe = Classes.objects.create(
            name="Classe Test Email",
            teacher=teacher,
            level=level
        )
        print(f"✅ Classe créée: {classe.name}")
        
        # Envoyer l'email
        print(f"\n🔧 Envoi de l'email au professeur...")
        result = send_teacher_class_assignment_email(teacher, classe, is_new_assignment=True)
        
        if result:
            print("✅ Email envoyé avec succès au professeur!")
            print("   Vérifiez votre boîte de réception (et les spams)")
            
            # Nettoyer
            response = input("\nNettoyer les données de test ? (o/N): ").strip().lower()
            if response == 'o':
                classe.delete()
                teacher.delete()
                if created:
                    level.delete()
                print("✅ Données de test nettoyées")
            else:
                print("⚠️  Données de test conservées")
            
            return True
        else:
            print("❌ Échec de l'envoi de l'email")
            
            # Nettoyer
            classe.delete()
            teacher.delete()
            if created:
                level.delete()
            
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("TESTS DES NOUVELLES FONCTIONNALITÉS")
    print("=" * 60)
    
    # Test 1: Unicité de l'email
    test1_result = test_email_uniqueness()
    
    # Test 2: Email au professeur
    test2_result = test_teacher_email()
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Test 1 - Unicité de l'email: {'✅ RÉUSSI' if test1_result else '❌ ÉCHOUÉ'}")
    print(f"Test 2 - Email au professeur: {'✅ RÉUSSI' if test2_result else '❌ ÉCHOUÉ'}")
    
    if test1_result and test2_result:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
    else:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

