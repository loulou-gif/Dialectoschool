# 📊 API Documentation - Gestion des Notes des Élèves

## Vue d'ensemble

L'API `/api/result-homework/` a été **corrigée et améliorée** pour retourner correctement les résultats des élèves avec toutes les informations détaillées (notes, devoirs, cours, etc.).

---

## 🔧 Corrections Appliquées

### 1. **Correction du bug principal**
- **Problème** : La vue retournait tous les résultats pour les étudiants au lieu de filtrer leurs propres notes
- **Solution** : Filtrage correct par `student=user` pour les étudiants authentifiés

### 2. **Amélioration du Serializer**
Nouveaux champs ajoutés :
- `student_email` : Email de l'étudiant
- `homework_description` : Description du devoir
- `course_name` : Nom du cours associé
- `level_name` : Niveau de la classe

### 3. **Optimisation des performances**
- Ajout de `select_related()` pour réduire les requêtes SQL
- Tri automatique par date décroissante (`-created_at`)

---

## 📡 Endpoints Disponibles

### 1. **Lister tous les résultats**
```http
GET /api/result-homework/
```

**Réponse** :
```json
[
  {
    "id": 1,
    "student": 5,
    "student_name": "Jean Dupont",
    "student_email": "jean.dupont@example.com",
    "class_name": 2,
    "classes_name": "Terminale A",
    "homework": 3,
    "homework_name": "Devoir de Mathématiques",
    "homework_description": "Exercices sur les intégrales",
    "course_name": "Mathématiques",
    "level_name": "Terminale",
    "result": 16,
    "observation": "Très bon travail, continue comme ça !",
    "created_at": "2025-10-22T10:30:00Z",
    "created_at_formatted": "22/10/2025 10:30"
  }
]
```

**Comportement selon le rôle** :
- **Admin/Teacher** : Voit tous les résultats
- **Student** : Voit uniquement ses propres résultats
- **Non authentifié** : Voit tous les résultats (si `AllowAny`)

---

### 2. **Obtenir un résultat spécifique**
```http
GET /api/result-homework/{id}/
```

**Exemple** :
```bash
GET /api/result-homework/1/
```

---

### 3. **Résultats par étudiant**
```http
GET /api/result-homework/by-student/{student_id}/
```

**Exemple** :
```bash
GET /api/result-homework/by-student/5/
```

**Réponse** :
```json
{
  "student_id": 5,
  "student_name": "Jean Dupont",
  "results": [
    {
      "id": 1,
      "homework_name": "Devoir de Maths",
      "result": 16,
      "observation": "Très bon travail",
      "created_at_formatted": "22/10/2025 10:30"
    }
  ],
  "total_results": 1
}
```

---

### 4. **Résultats par classe**
```http
GET /api/result-homework/by-class/{class_id}/
```

**Exemple** :
```bash
GET /api/result-homework/by-class/2/
```

**Réponse** :
```json
{
  "class_id": 2,
  "class_name": "Terminale A",
  "results": [
    {
      "student_name": "Jean Dupont",
      "homework_name": "Devoir de Maths",
      "result": 16
    },
    {
      "student_name": "Marie Martin",
      "homework_name": "Devoir de Maths",
      "result": 18
    }
  ],
  "total_results": 2
}
```

---

### 5. **Résultats par devoir**
```http
GET /api/result-homework/by-homework/{homework_id}/
```

**Exemple** :
```bash
GET /api/result-homework/by-homework/3/
```

**Réponse** :
```json
{
  "homework_id": 3,
  "homework_name": "Devoir de Mathématiques",
  "results": [
    {
      "student_name": "Jean Dupont",
      "result": 16,
      "observation": "Très bon"
    },
    {
      "student_name": "Marie Martin",
      "result": 18,
      "observation": "Excellent"
    }
  ],
  "total_results": 2
}
```

---

### 6. **Statistiques générales**
```http
GET /api/result-homework/statistics/
```

**Réponse** :
```json
{
  "total_results": 50,
  "average_score": 14.75,
  "highest_score": 20,
  "lowest_score": 8
}
```

---

### 7. **Créer une nouvelle note**
```http
POST /api/result-homework/
Content-Type: application/json
```

**Body** :
```json
{
  "student": 5,
  "class_name": 2,
  "homework": 3,
  "result": 16,
  "observation": "Très bon travail, continue !"
}
```

**Actions automatiques** :
- ✉️ Envoi d'un email à l'étudiant avec sa note
- 📝 Enregistrement de la note en base de données

---

### 8. **Mettre à jour une note**
```http
PUT /api/result-homework/{id}/
Content-Type: application/json
```

**Body** :
```json
{
  "result": 18,
  "observation": "Excellent travail !"
}
```

**Actions automatiques** :
- ✉️ Envoi d'un email si la note change

---

### 9. **Supprimer une note**
```http
DELETE /api/result-homework/{id}/
```

---

## 💻 Exemples d'utilisation

### JavaScript (Fetch API)

```javascript
// Lister toutes les notes
fetch('http://localhost:8000/api/result-homework/')
  .then(response => response.json())
  .then(data => console.log(data));

// Obtenir les notes d'un étudiant
fetch('http://localhost:8000/api/result-homework/by-student/5/')
  .then(response => response.json())
  .then(data => {
    console.log(`Étudiant: ${data.student_name}`);
    console.log(`Total de notes: ${data.total_results}`);
    data.results.forEach(result => {
      console.log(`${result.homework_name}: ${result.result}/20`);
    });
  });

// Créer une nouvelle note
fetch('http://localhost:8000/api/result-homework/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    student: 5,
    class_name: 2,
    homework: 3,
    result: 16,
    observation: "Très bon travail"
  })
})
.then(response => response.json())
.then(data => console.log('Note créée:', data));

// Obtenir les statistiques
fetch('http://localhost:8000/api/result-homework/statistics/')
  .then(response => response.json())
  .then(stats => {
    console.log(`Moyenne générale: ${stats.average_score}`);
    console.log(`Meilleure note: ${stats.highest_score}`);
  });
```

### Python (requests)

```python
import requests

base_url = "http://localhost:8000"

# Lister toutes les notes
response = requests.get(f"{base_url}/api/result-homework/")
results = response.json()
print(results)

# Obtenir les notes d'un étudiant
response = requests.get(f"{base_url}/api/result-homework/by-student/5/")
data = response.json()
print(f"Étudiant: {data['student_name']}")
print(f"Total de notes: {data['total_results']}")

# Créer une nouvelle note
new_result = {
    "student": 5,
    "class_name": 2,
    "homework": 3,
    "result": 16,
    "observation": "Très bon travail"
}
response = requests.post(
    f"{base_url}/api/result-homework/",
    json=new_result
)
print(response.json())
```

### cURL

```bash
# Lister toutes les notes
curl http://localhost:8000/api/result-homework/

# Obtenir les notes d'un étudiant
curl http://localhost:8000/api/result-homework/by-student/5/

# Créer une nouvelle note
curl -X POST http://localhost:8000/api/result-homework/ \
  -H "Content-Type: application/json" \
  -d '{
    "student": 5,
    "class_name": 2,
    "homework": 3,
    "result": 16,
    "observation": "Très bon travail"
  }'

# Obtenir les statistiques
curl http://localhost:8000/api/result-homework/statistics/
```

---

## 🎯 Cas d'usage typiques

### 1. **Dashboard enseignant - Voir toutes les notes de sa classe**
```javascript
const classId = 2;
fetch(`http://localhost:8000/api/result-homework/by-class/${classId}/`)
  .then(response => response.json())
  .then(data => {
    displayClassResults(data.results);
  });
```

### 2. **Espace étudiant - Voir ses propres notes**
```javascript
// L'API filtre automatiquement pour l'étudiant connecté
fetch('http://localhost:8000/api/result-homework/')
  .then(response => response.json())
  .then(myResults => {
    displayMyGrades(myResults);
  });
```

### 3. **Correction de devoir - Voir toutes les copies d'un devoir**
```javascript
const homeworkId = 3;
fetch(`http://localhost:8000/api/result-homework/by-homework/${homeworkId}/`)
  .then(response => response.json())
  .then(data => {
    data.results.forEach(result => {
      console.log(`${result.student_name}: ${result.result}/20`);
    });
  });
```

### 4. **Tableau de bord admin - Statistiques globales**
```javascript
fetch('http://localhost:8000/api/result-homework/statistics/')
  .then(response => response.json())
  .then(stats => {
    document.getElementById('average').textContent = stats.average_score;
    document.getElementById('total').textContent = stats.total_results;
  });
```

---

## 🔐 Sécurité et Permissions

**Actuellement** : `permission_classes = [AllowAny]`
- Tous les endpoints sont accessibles sans authentification
- Utile pour le développement

**Pour la production**, vous devriez modifier vers :
```python
permission_classes = [IsAuthenticated]
```

Et ajouter des vérifications de rôles dans les actions personnalisées.

---

## 📝 Structure complète d'un résultat

```json
{
  "id": 1,
  "student": 5,
  "student_name": "Jean Dupont",
  "student_email": "jean.dupont@example.com",
  "class_name": 2,
  "classes_name": "Terminale A",
  "homework": 3,
  "homework_name": "Devoir de Mathématiques",
  "homework_description": "Exercices sur les intégrales",
  "course_name": "Mathématiques",
  "level_name": "Terminale",
  "result": 16,
  "observation": "Très bon travail, continue comme ça !",
  "created_at": "2025-10-22T10:30:00Z",
  "created_at_formatted": "22/10/2025 10:30"
}
```

---

## ✅ Résumé des améliorations

| Amélioration | Avant | Après |
|-------------|-------|-------|
| **Bug de filtrage** | Tous les résultats pour étudiants | ✅ Filtrage correct par étudiant |
| **Informations** | Basiques | ✅ Détails complets (cours, niveau, description) |
| **Performance** | N+1 queries | ✅ Optimisé avec `select_related()` |
| **Endpoints** | 1 seul | ✅ 6 endpoints spécialisés |
| **Statistiques** | Aucune | ✅ API dédiée aux statistiques |

---

## 🚀 Démarrer le serveur

```bash
cd dialectoskoul
python manage.py runserver
```

L'API sera accessible sur : **http://localhost:8000/api/result-homework/**

---

## 📞 Support

Si vous rencontrez des problèmes, vérifiez :
1. ✅ Le serveur Django est bien démarré
2. ✅ Les migrations sont à jour : `python manage.py migrate`
3. ✅ Les données existent en base de données
4. ✅ L'URL est correcte (avec le `/` final)

---

**Date de mise à jour** : 22 octobre 2025
**Version de l'API** : 2.0 (Améliorée)

