# 📧 Système d'Email de Bienvenue - DialectosKoul

## 🎯 Fonctionnalités Implémentées

Le système d'envoi d'email de bienvenue a été intégré à votre application **sans modifier** la logique existante qui fonctionne déjà.

### ✅ Ce qui a été ajouté :

1. **Template HTML de bienvenue** (`skoulApi/templates/email/welcome.html`)
   - Design moderne et professionnel
   - Affiche les identifiants de connexion (login + mot de passe)
   - Message personnalisé selon le rôle de l'utilisateur
   - Bouton de connexion direct

2. **Fonction d'envoi d'email** (`send_welcome_email()` dans `services.py`)
   - Envoie automatiquement un email lors de la création d'un utilisateur
   - Version HTML + version texte brut (fallback)
   - Sauvegarde l'email dans la base de données pour traçabilité
   - Gestion d'erreur robuste

3. **Intégration dans le serializer** (`UserSerializer` dans `serializers.py`)
   - Envoi automatique lors de la création d'un utilisateur
   - N'échoue pas si l'email ne peut pas être envoyé
   - Ne modifie pas la logique existante

## 📋 Ce qui est envoyé dans l'email :

- **Nom de l'utilisateur** (prénom + nom ou username)
- **Nom d'utilisateur** (login)
- **Adresse email**
- **Mot de passe en clair** (avant hachage)
- **Rôle** (Administrateur/Enseignant/Étudiant)
- **Lien de connexion** (à personnaliser)

## 🔧 Configuration

### Personnaliser le lien de connexion :

Dans `skoulApi/services.py`, ligne 87 :
```python
'login_link': 'http://localhost:5500/login.html',  # À personnaliser selon votre frontend
```

### Personnaliser le template :

Modifiez le fichier `skoulApi/templates/email/welcome.html` selon vos besoins.

## 🧪 Test

Pour tester l'envoi d'email de bienvenue sans créer un vrai utilisateur :

```bash
cd dialectoskoul
python test_welcome_email.py
```

Le script vous demandera votre email de test et enverra un email de démonstration.

## 📝 Utilisation

### Création d'utilisateur via l'API :

```bash
POST /api/users/
{
    "username": "nouveau_user",
    "email": "user@example.com",
    "password": "MotDePasse123!",
    "first_name": "Prénom",
    "last_name": "Nom",
    "role": "student"
}
```

➡️ **L'email de bienvenue sera envoyé automatiquement** après la création

### Comportement :

1. ✅ L'utilisateur est créé dans la base de données
2. ✅ Le mot de passe est haché de manière sécurisée
3. ✅ Un email de bienvenue est envoyé avec les identifiants
4. ✅ L'email est enregistré dans `EmailSendModel` pour traçabilité
5. ✅ En cas d'échec de l'email, la création continue (pas de blocage)

## 🔍 Logs

Les logs des emails sont sauvegardés dans :
- **Console** : logs en temps réel
- **Fichier** : `email_logs.log`
- **Base de données** : table `EmailSendModel`

## ⚠️ Important

- **Sécurité** : Le mot de passe en clair est envoyé par email. Recommandez aux utilisateurs de le changer à la première connexion.
- **SMTP** : Assurez-vous que la configuration SMTP est correcte dans `settings.py`
- **Template** : Le template utilise le fichier `base.html` existant

## 🎨 Personnalisation du Template

Le template de bienvenue hérite de `email/base.html` qui contient :
- Header avec logo
- Footer avec copyright
- Styles CSS responsive

Vous pouvez personnaliser :
- Les couleurs
- Le logo (dans `base.html`)
- Le texte du message
- Les informations affichées

## 📊 Traçabilité

Chaque email envoyé est enregistré dans la base de données avec :
- Sujet
- Contenu
- Destinataire
- Date d'envoi
- Criticité

Vous pouvez consulter l'historique via l'API :
```bash
GET /api/emails/
```

## 🚀 Prochaines Étapes Possibles

1. **Email de réinitialisation de mot de passe**
2. **Email de notification pour les devoirs**
3. **Email de rappel pour les cours**
4. **Email de notification pour les notes**
5. **Email de confirmation d'inscription à un cours**

---

**Fait le** : 7 Octobre 2025  
**Status** : ✅ Opérationnel
