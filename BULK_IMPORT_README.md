# 📚 Services d'Import en Masse - DialectosKoul

## Date : 9 Octobre 2025

---

## ✅ Fonctionnalités Implémentées

### 1. 👥 Import en Masse d'Utilisateurs (Excel)
### 2. 🎓 Affectation en Masse d'Étudiants (JSON ou Excel)

---

## 📋 Service 1 : Import en Masse d'Utilisateurs

### 🎯 Description

Ce service permet de créer ou mettre à jour plusieurs utilisateurs en une seule fois en important un fichier Excel.

### 🔗 Endpoint

```
POST /api/bulk-create-users/
```

### 📄 Format du Fichier Excel

Le fichier Excel doit contenir les colonnes suivantes (en-tête obligatoire) :

| Colonne | Type | Obligatoire | Description |
|---------|------|-------------|-------------|
| `username` | Texte | ✅ Oui | Nom d'utilisateur unique |
| `email` | Email | ✅ Oui | Adresse email |
| `password` | Texte | ✅ Oui | Mot de passe (sera envoyé par email) |
| `first_name` | Texte | ❌ Non | Prénom |
| `last_name` | Texte | ❌ Non | Nom de famille |
| `role` | Texte | ✅ Oui | Rôle : `student`, `teacher`, ou `admin` |

### 📊 Exemple de Fichier Excel

| username | email | password | first_name | last_name | role |
|----------|-------|----------|------------|-----------|------|
| jean_dupont | jean.dupont@example.com | Pass123! | Jean | Dupont | student |
| marie_martin | marie.martin@example.com | Marie456! | Marie | Martin | student |
| prof_math | prof.math@example.com | Prof789! | Pierre | Bernard | teacher |
| admin_user | admin@example.com | Admin000! | Admin | System | admin |

### 📤 Requête cURL

```bash
curl -X POST http://localhost:8000/api/bulk-create-users/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@utilisateurs.xlsx"
```

### 📥 Réponse

```json
{
  "success": true,
  "message": "Import terminé",
  "statistics": {
    "total_rows": 4,
    "created": 3,
    "updated": 1,
    "failed": 0
  },
  "created_users": [
    {
      "row": 2,
      "username": "jean_dupont",
      "email": "jean.dupont@example.com",
      "role": "student"
    },
    {
      "row": 3,
      "username": "marie_martin",
      "email": "marie.martin@example.com",
      "role": "student"
    },
    {
      "row": 4,
      "username": "prof_math",
      "email": "prof.math@example.com",
      "role": "teacher"
    }
  ],
  "updated_users": [
    {
      "row": 5,
      "username": "admin_user",
      "email": "admin@example.com",
      "role": "admin"
    }
  ],
  "failed_users": []
}
```

### 📧 Emails Automatiques

Pour **chaque nouvel utilisateur créé**, un email de bienvenue est automatiquement envoyé avec :
- ✅ Identifiants de connexion (username et password)
- ✅ Rôle assigné
- ✅ Lien vers la plateforme

Pour les **utilisateurs mis à jour**, aucun email n'est envoyé.

### ⚠️ Comportement

1. **Utilisateur existant** (même username) :
   - ✅ Les informations sont mises à jour
   - ✅ Le mot de passe est changé
   - ❌ Aucun email n'est envoyé

2. **Nouvel utilisateur** :
   - ✅ L'utilisateur est créé
   - ✅ Un email de bienvenue est envoyé

3. **Erreurs** :
   - Les erreurs sont reportées dans `failed_users`
   - Les autres utilisateurs sont quand même créés/mis à jour

---

## 📋 Service 2 : Affectation en Masse d'Étudiants

### 🎯 Description

Ce service permet d'affecter plusieurs étudiants à une classe en une seule fois, soit via JSON, soit via un fichier Excel.

### 🔗 Endpoint

```
POST /api/bulk-assign-students/
```

### 📝 Méthode 1 : Par JSON (Liste d'IDs)

#### Requête

```json
{
  "class_id": 5,
  "student_ids": [1, 2, 3, 4, 5]
}
```

#### Exemple cURL

```bash
curl -X POST http://localhost:8000/api/bulk-assign-students/ \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": 5,
    "student_ids": [1, 2, 3, 4, 5]
  }'
```

### 📄 Méthode 2 : Par Fichier Excel

#### Format du Fichier Excel

Le fichier doit contenir **au moins une** des colonnes suivantes :

| Colonne | Type | Description |
|---------|------|-------------|
| `student_id` | Nombre | ID de l'étudiant |
| `student_username` | Texte | Nom d'utilisateur de l'étudiant |
| `student_email` | Email | Email de l'étudiant |

**Note :** Une seule colonne suffit pour identifier les étudiants.

#### Exemple de Fichier Excel (par ID)

| student_id |
|------------|
| 1 |
| 2 |
| 3 |
| 4 |
| 5 |

#### Exemple de Fichier Excel (par Username)

| student_username |
|------------------|
| jean_dupont |
| marie_martin |
| paul_durand |
| sophie_bernard |

#### Exemple de Fichier Excel (par Email)

| student_email |
|---------------|
| jean.dupont@example.com |
| marie.martin@example.com |
| paul.durand@example.com |

#### Requête cURL avec Excel

```bash
curl -X POST http://localhost:8000/api/bulk-assign-students/ \
  -H "Content-Type: multipart/form-data" \
  -F "class_id=5" \
  -F "file=@etudiants.xlsx"
```

### 📥 Réponse

```json
{
  "success": true,
  "message": "Affectation en masse terminée",
  "class": {
    "id": 5,
    "name": "Classe 6ème A",
    "level": "6ème"
  },
  "statistics": {
    "total_students": 5,
    "assigned": 3,
    "updated": 2,
    "failed": 0
  },
  "assigned_students": [
    {
      "student_id": 1,
      "username": "jean_dupont",
      "email": "jean.dupont@example.com",
      "class": "Classe 6ème A"
    },
    {
      "student_id": 2,
      "username": "marie_martin",
      "email": "marie.martin@example.com",
      "class": "Classe 6ème A"
    },
    {
      "student_id": 3,
      "username": "paul_durand",
      "email": "paul.durand@example.com",
      "class": "Classe 6ème A"
    }
  ],
  "updated_students": [
    {
      "student_id": 4,
      "username": "sophie_bernard",
      "email": "sophie.bernard@example.com",
      "old_class": "Classe 5ème B",
      "new_class": "Classe 6ème A"
    },
    {
      "student_id": 5,
      "username": "lucas_petit",
      "email": "lucas.petit@example.com",
      "old_class": "Classe 5ème C",
      "new_class": "Classe 6ème A"
    }
  ],
  "failed_students": []
}
```

### 📧 Emails Automatiques

Pour **chaque étudiant affecté**, un email est automatiquement envoyé avec :

1. **Nouvelle affectation** :
   - ✅ Informations de la classe (nom, niveau, professeur)
   - ✅ Liste des cours disponibles
   - ✅ Lien vers l'espace étudiant

2. **Réaffectation** (changement de classe) :
   - ✅ Informations de la nouvelle classe
   - ✅ Liste des nouveaux cours disponibles
   - ✅ Lien vers l'espace étudiant

### ⚠️ Comportement

1. **Étudiant déjà affecté à une classe** :
   - ✅ L'affectation est mise à jour vers la nouvelle classe
   - ✅ Un email de réaffectation est envoyé

2. **Étudiant non affecté** :
   - ✅ Une nouvelle affectation est créée
   - ✅ Un email d'affectation est envoyé

3. **Erreurs** :
   - Les erreurs sont reportées dans `failed_students`
   - Les autres étudiants sont quand même affectés

---

## 🧪 Tests

### Test Import d'Utilisateurs

1. Créer un fichier Excel `test_users.xlsx` avec le format décrit ci-dessus
2. Exécuter la requête :

```bash
curl -X POST http://localhost:8000/api/bulk-create-users/ \
  -F "file=@test_users.xlsx"
```

3. Vérifier :
   - ✅ Les utilisateurs sont créés dans la base de données
   - ✅ Les emails de bienvenue sont envoyés
   - ✅ La réponse contient les statistiques

### Test Affectation d'Étudiants (JSON)

1. Récupérer les IDs d'étudiants et d'une classe
2. Exécuter la requête :

```bash
curl -X POST http://localhost:8000/api/bulk-assign-students/ \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": 5,
    "student_ids": [1, 2, 3]
  }'
```

3. Vérifier :
   - ✅ Les étudiants sont affectés à la classe
   - ✅ Les emails d'affectation sont envoyés
   - ✅ La réponse contient les statistiques

### Test Affectation d'Étudiants (Excel)

1. Créer un fichier Excel `test_students.xlsx` avec une colonne `student_id` ou `student_username`
2. Exécuter la requête :

```bash
curl -X POST http://localhost:8000/api/bulk-assign-students/ \
  -F "class_id=5" \
  -F "file=@test_students.xlsx"
```

3. Vérifier :
   - ✅ Les étudiants sont affectés à la classe
   - ✅ Les emails d'affectation sont envoyés
   - ✅ La réponse contient les statistiques

---

## ⚙️ Configuration

### Dépendances Installées

```txt
openpyxl==3.0.9  # Pour lire les fichiers Excel (.xlsx)
pandas==1.3.5    # Pour manipuler les données Excel
```

### Fichiers Créés/Modifiés

**Nouveaux services :**
- ✅ `skoulApi/views.py` - Fonctions `bulk_create_users_from_excel()` et `bulk_assign_students_to_class()`

**Nouveaux endpoints :**
- ✅ `dialectoskoul/urls.py` - Routes `/api/bulk-create-users/` et `/api/bulk-assign-students/`

**Documentation :**
- ✅ `BULK_IMPORT_README.md` (ce fichier)

---

## 🔒 Sécurité

### Permissions

- **Import d'utilisateurs** : `AllowAny` (à modifier selon vos besoins)
- **Affectation d'étudiants** : `AllowAny` (à modifier selon vos besoins)

**⚠️ Recommandation** : Changez les permissions pour restreindre l'accès aux administrateurs uniquement :

```python
@permission_classes([IsAuthenticated, IsAdminUser])
```

### Validation

1. **Fichiers Excel** :
   - ✅ Vérification de l'extension (.xlsx ou .xls)
   - ✅ Validation des colonnes requises

2. **Données** :
   - ✅ Validation des champs obligatoires
   - ✅ Vérification de l'existence de la classe
   - ✅ Vérification du rôle de l'utilisateur

3. **Emails** :
   - ✅ Vérification de l'email avant envoi
   - ✅ Gestion des erreurs d'envoi (non-bloquant)

---

## 📈 Statistiques Retournées

Les deux services retournent des statistiques détaillées :

### Import d'Utilisateurs

```json
{
  "statistics": {
    "total_rows": 10,      // Nombre total de lignes dans le fichier
    "created": 7,          // Nouveaux utilisateurs créés
    "updated": 2,          // Utilisateurs existants mis à jour
    "failed": 1            // Échecs (avec détails dans failed_users)
  }
}
```

### Affectation d'Étudiants

```json
{
  "statistics": {
    "total_students": 10,  // Nombre total d'étudiants traités
    "assigned": 6,         // Nouvelles affectations
    "updated": 3,          // Réaffectations (changement de classe)
    "failed": 1            // Échecs (avec détails dans failed_students)
  }
}
```

---

## ❌ Gestion des Erreurs

### Erreurs Possibles

1. **Fichier invalide** :
```json
{
  "error": "Format de fichier invalide",
  "message": "Le fichier doit être au format Excel (.xlsx ou .xls)"
}
```

2. **Colonnes manquantes** :
```json
{
  "error": "Colonnes manquantes",
  "message": "Les colonnes suivantes sont requises : username, email, password, role",
  "columns_found": ["username", "email"]
}
```

3. **Classe non trouvée** :
```json
{
  "error": "Classe non trouvée",
  "class_id": 99
}
```

4. **Erreur de lecture** :
```json
{
  "error": "Erreur lors de la lecture du fichier",
  "message": "Détails de l'erreur"
}
```

---

## 💡 Bonnes Pratiques

### Import d'Utilisateurs

1. **Préparez votre fichier Excel** :
   - ✅ Utilisez les en-têtes exactes (respectez la casse)
   - ✅ Évitez les cellules vides dans les colonnes obligatoires
   - ✅ Utilisez des mots de passe forts

2. **Testez d'abord avec peu d'utilisateurs** :
   - Importez 2-3 utilisateurs pour vérifier le format
   - Vérifiez que les emails sont bien envoyés

3. **Sauvegardez votre fichier** :
   - Gardez une copie du fichier Excel
   - Utilisez des noms de fichiers explicites (ex: `users_2025_10_09.xlsx`)

### Affectation d'Étudiants

1. **Vérifiez les IDs** :
   - Assurez-vous que les IDs d'étudiants existent
   - Vérifiez que la classe existe

2. **Utilisez la méthode appropriée** :
   - **JSON** : Rapide pour quelques étudiants (< 20)
   - **Excel** : Pratique pour beaucoup d'étudiants (> 20)

3. **Vérifiez les résultats** :
   - Consultez `assigned_students` et `updated_students`
   - Vérifiez `failed_students` pour les erreurs

---

## 🚀 Améliorations Futures

### Possibilités d'Extension

1. **Sécurité** :
   - 🔒 Restriction d'accès aux administrateurs
   - 🔐 Authentification obligatoire
   - 📝 Logging des imports

2. **Fonctionnalités** :
   - 📊 Export des résultats en Excel
   - 📧 Email récapitulatif à l'administrateur
   - 🔄 Validation préalable (dry-run)
   - 📅 Planification d'imports différés

3. **Interface** :
   - 🖥️ Interface web pour l'upload
   - 📈 Barre de progression
   - 📄 Aperçu du fichier avant import

---

## 📊 Résumé

### ✅ Ce qui fonctionne maintenant

1. **Import en masse d'utilisateurs** :
   - ✅ Création de plusieurs utilisateurs depuis Excel
   - ✅ Mise à jour d'utilisateurs existants
   - ✅ Envoi automatique d'emails de bienvenue
   - ✅ Statistiques détaillées
   - ✅ Gestion robuste des erreurs

2. **Affectation en masse d'étudiants** :
   - ✅ Affectation par JSON (liste d'IDs)
   - ✅ Affectation par Excel (ID, username, ou email)
   - ✅ Réaffectation automatique si déjà dans une classe
   - ✅ Envoi automatique d'emails d'affectation/réaffectation
   - ✅ Statistiques détaillées
   - ✅ Gestion robuste des erreurs

### 🎓 Bénéfices

- ⏱️ **Gain de temps** : Importez des centaines d'utilisateurs en quelques secondes
- 📧 **Automatisation** : Emails envoyés automatiquement
- 📊 **Traçabilité** : Statistiques complètes de chaque import
- 🛡️ **Robustesse** : Gestion des erreurs sans perte de données
- 🔄 **Flexibilité** : Plusieurs méthodes d'import disponibles

---

**Status** : ✅ **OPÉRATIONNEL**  
**Testé** : ✅ **OUI**  
**Intégré** : ✅ **COMPLET**

---

**Fait le** : 9 Octobre 2025  
**Développeur** : Assistant IA


