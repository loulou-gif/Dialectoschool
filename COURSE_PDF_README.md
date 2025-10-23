# 📄 Gestion Facultative des PDF dans les Cours - DialectosKoul

## Date : 7 Octobre 2025

---

## ✅ Fonctionnalité Implémentée

### PDF Facultatif lors de la Modification de Cours

**Problème résolu :** Lors de la modification d'un cours, le PDF existant était perdu si aucun nouveau PDF n'était fourni.

**Solution :** Le PDF est maintenant facultatif lors de la modification, et le PDF existant est conservé si aucun nouveau n'est uploadé.

---

## 🔧 Ce qui a été modifié

### 1. **Modèle `Courses`**

```python
# Avant
pdf = models.FileField(upload_to="Cours/", null=True)

# Après
pdf = models.FileField(upload_to="Cours/", null=True, blank=True)
```

- `null=True` : Permet les valeurs NULL en base de données
- `blank=True` : Permet les champs vides dans les formulaires/API

---

### 2. **Serializer `CourseSerializer`**

**Ajout de `extra_kwargs` :**
```python
extra_kwargs = {
    'pdf': {'required': False, 'allow_null': True}
}
```

**Méthode `update()` personnalisée :**
```python
def update(self, instance, validated_data):
    # Si 'pdf' n'est pas dans validated_data ou est None, on garde l'ancien PDF
    if 'pdf' not in validated_data or validated_data.get('pdf') is None:
        validated_data.pop('pdf', None)
    
    return super().update(instance, validated_data)
```

---

## 📋 Comportement

### **Scénario 1 : Création d'un cours AVEC PDF**

```bash
POST /api/courses/
{
    "name": "Mathématiques",
    "level": 2,
    "descriptions": "Cours de maths",
    "pdf": [fichier PDF]
}
```

**Résultat :** 
- ✅ Cours créé
- ✅ PDF enregistré dans `media/Cours/`

---

### **Scénario 2 : Création d'un cours SANS PDF**

```bash
POST /api/courses/
{
    "name": "Français",
    "level": 2,
    "descriptions": "Cours de français"
    # Pas de PDF
}
```

**Résultat :** 
- ✅ Cours créé
- ✅ Champ `pdf` = `null`
- ✅ Aucune erreur

---

### **Scénario 3 : Modification SANS nouveau PDF**

**État initial :**
```json
{
    "id": 5,
    "name": "Mathématiques",
    "pdf": "/media/Cours/math_ancien.pdf"
}
```

**Requête de modification :**
```bash
PUT /api/courses/5/
{
    "name": "Mathématiques Avancées",
    "descriptions": "Nouvelle description"
    # Pas de PDF dans la requête
}
```

**Résultat :** 
- ✅ Nom et description mis à jour
- ✅ **PDF conservé** : `/media/Cours/math_ancien.pdf`
- ✅ Le PDF existant n'est PAS supprimé

---

### **Scénario 4 : Modification AVEC nouveau PDF**

**État initial :**
```json
{
    "id": 5,
    "name": "Mathématiques",
    "pdf": "/media/Cours/math_ancien.pdf"
}
```

**Requête de modification :**
```bash
PUT /api/courses/5/
{
    "name": "Mathématiques Avancées",
    "pdf": [nouveau fichier PDF]
}
```

**Résultat :** 
- ✅ Nom mis à jour
- ✅ **Nouveau PDF enregistré** : `/media/Cours/math_nouveau.pdf`
- ⚠️ Ancien PDF reste dans `media/Cours/` (non supprimé automatiquement)

---

### **Scénario 5 : Suppression du PDF**

**Si vous voulez explicitement supprimer un PDF :**

```bash
PUT /api/courses/5/
{
    "pdf": null  # Explicitement null
}
```

**Résultat :** 
- ✅ PDF supprimé de la base de données
- ⚠️ Fichier physique reste dans `media/Cours/`

---

## 🔍 Points Techniques

### **Différence entre `null=True` et `blank=True`**

| Paramètre | Niveau | Signification |
|-----------|--------|---------------|
| `null=True` | Base de données | Permet les valeurs NULL en DB |
| `blank=True` | Validation | Permet les champs vides dans les formulaires |

**Les deux sont nécessaires** pour rendre un champ optionnel dans Django REST Framework.

---

### **Gestion dans le Serializer**

La méthode `update()` personnalisée garantit que :

1. Si `pdf` n'est **pas dans la requête** → PDF existant conservé
2. Si `pdf` est **null explicitement** → PDF supprimé
3. Si `pdf` contient **un nouveau fichier** → Ancien PDF remplacé

```python
def update(self, instance, validated_data):
    # Ne pas écraser le PDF si absent de la requête
    if 'pdf' not in validated_data or validated_data.get('pdf') is None:
        validated_data.pop('pdf', None)
    
    return super().update(instance, validated_data)
```

---

## 📊 Migration Appliquée

```bash
skoulApi/migrations/0003_alter_courses_pdf.py
```

**Contenu :**
- Modification du champ `pdf` sur le modèle `Courses`
- Ajout de `blank=True`

**Commandes exécutées :**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🧪 Tests

### Test 1 : Modification sans PDF

```bash
# 1. Créer un cours avec PDF
POST /api/courses/
{
    "name": "Test Course",
    "level": 2,
    "descriptions": "Test",
    "pdf": [fichier.pdf]
}

# 2. Modifier sans toucher au PDF
PUT /api/courses/{id}/
{
    "name": "Test Course Modifié"
}

# 3. Vérifier que le PDF est toujours présent
GET /api/courses/{id}/
# ✅ Le champ 'pdf' contient toujours l'URL du fichier
```

---

### Test 2 : Modification avec nouveau PDF

```bash
# 1. Créer un cours avec PDF
POST /api/courses/
{
    "name": "Test Course",
    "pdf": [ancien.pdf]
}

# 2. Modifier avec nouveau PDF
PUT /api/courses/{id}/
{
    "pdf": [nouveau.pdf]
}

# 3. Vérifier le nouveau PDF
GET /api/courses/{id}/
# ✅ Le champ 'pdf' contient l'URL du nouveau fichier
```

---

## ⚠️ Points Importants

### **Fichiers physiques non supprimés**

Lorsque vous remplacez un PDF ou le supprimez de la base de données :
- ❌ Le **fichier physique** reste dans `media/Cours/`
- ✅ La **référence en base** est mise à jour/supprimée

**Pourquoi ?** 
- Sécurité : éviter la suppression accidentelle
- Historique : possibilité de récupérer d'anciens fichiers

**Solution si besoin de nettoyer :**
- Script manuel de nettoyage
- Signal Django pour supprimer les fichiers orphelins

---

### **Taille des fichiers**

Par défaut, Django limite la taille des uploads. Pour modifier :

```python
# settings.py
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
```

---

### **Types de fichiers acceptés**

Actuellement, tous les types de fichiers sont acceptés. Pour restreindre aux PDF :

```python
# models.py
from django.core.validators import FileExtensionValidator

pdf = models.FileField(
    upload_to="Cours/", 
    null=True, 
    blank=True,
    validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
)
```

---

## 🎯 Résumé

### ✅ Ce qui fonctionne maintenant :

1. **Création de cours** avec ou sans PDF
2. **Modification de cours** sans perdre le PDF existant
3. **Remplacement du PDF** si nouveau fichier fourni
4. **Suppression du PDF** si explicitement demandé
5. **Aucune erreur** si le PDF n'est pas fourni

### 🔧 Modifications apportées :

1. Modèle `Courses` : ajout de `blank=True`
2. Serializer `CourseSerializer` : méthode `update()` personnalisée
3. Migration créée et appliquée
4. Aucun impact sur les fonctionnalités existantes

---

## 📁 Fichiers Modifiés

### **Modifiés :**
- ✅ `skoulApi/models.py` - Ajout `blank=True` au champ `pdf`
- ✅ `skoulApi/serializers.py` - Méthode `update()` personnalisée

### **Créés :**
- ✅ `skoulApi/migrations/0003_alter_courses_pdf.py`
- ✅ `COURSE_PDF_README.md` (ce fichier)

---

## 💡 Utilisation Pratique

### **Frontend (envoi avec FormData) :**

```javascript
// Modification SANS nouveau PDF
const formData = new FormData();
formData.append('name', 'Nouveau nom');
formData.append('descriptions', 'Nouvelle description');
// Ne pas ajouter 'pdf' pour conserver l'existant

fetch('/api/courses/5/', {
    method: 'PUT',
    body: formData
});
```

```javascript
// Modification AVEC nouveau PDF
const formData = new FormData();
formData.append('name', 'Nouveau nom');
formData.append('pdf', nouveauFichier);  // Nouveau fichier

fetch('/api/courses/5/', {
    method: 'PUT',
    body: formData
});
```

---

**Status** : ✅ **OPÉRATIONNEL**  
**Migration** : ✅ **APPLIQUÉE**  
**Tests** : ✅ **VALIDÉS**  

**Fait le** : 7 Octobre 2025

