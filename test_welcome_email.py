#!/usr/bin/env python
"""
Script de test pour l'envoi d'email de bienvenue
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dialectoskoul.settings')
django.setup()

from skoulApi.models import CustomUser
from skoulApi.services import send_welcome_email

def test_welcome_email():
    print("=" * 60)
    print("TEST D'ENVOI D'EMAIL DE BIENVENUE")
    print("=" * 60)
    
    # Demander l'email de test
    test_email = input("Entrez votre email pour le test: ").strip()
    if not test_email:
        print("Email requis pour le test")
        return False
    
    try:
        # Créer un utilisateur de test temporaire
        test_user = CustomUser(
            username="test_user_demo",
            first_name="Test",
            last_name="Utilisateur",
            email=test_email,
            role="student"
        )
        test_user.set_password("TestPassword123!")
        
        print(f"\nUtilisateur de test créé:")
        print(f"  - Nom d'utilisateur: {test_user.username}")
        print(f"  - Email: {test_user.email}")
        print(f"  - Rôle: {test_user.role}")
        
        # Envoyer l'email de bienvenue
        print(f"\nEnvoi de l'email de bienvenue...")
        result = send_welcome_email(test_user, "TestPassword123!")
        
        if result:
            print("✅ Email de bienvenue envoyé avec succès!")
            print("Vérifiez votre boîte de réception (et les spams)")
            return True
        else:
            print("❌ Échec de l'envoi de l'email de bienvenue")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Démarrage du test d'envoi d'email de bienvenue...")
    success = test_welcome_email()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 TEST RÉUSSI!")
        print("L'email de bienvenue a été envoyé avec succès.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ TEST ÉCHOUÉ")
        print("Vérifiez les logs dans email_logs.log")
        print("=" * 60)
