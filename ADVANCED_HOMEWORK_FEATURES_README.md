# Fonctionnalités Avancées des Devoirs

## Vue d'ensemble

Le système de devoirs a été étendu avec des fonctionnalités avancées pour répondre aux besoins spécifiques de l'éducation, notamment la gestion des étudiants malades et la sécurité d'accès aux formulaires.

## Nouvelles Fonctionnalités

### 1. Devoirs Individuels
- **Ciblage spécifique** : Possibilité de créer des devoirs pour un étudiant particulier
- **Cas d'usage** : Étudiants malades, rattrapages, devoirs personnalisés
- **Gestion automatique** : Le système détecte automatiquement si un devoir est individuel

### 2. Dates de Fin de Disponibilité
- **Limite temporelle** : Les devoirs peuvent avoir une date de fin
- **Gestion automatique** : Vérification automatique de la disponibilité
- **Sécurité** : Accès refusé aux devoirs expirés

### 3. Redirection Sécurisée
- **Sécurité renforcée** : Les liens directs vers Google Forms sont remplacés par des redirections via l'application
- **Contrôle d'accès** : Vérification des permissions avant l'accès au formulaire
- **Traçabilité** : Tous les accès passent par l'application

## Modifications du Modèle Homework

### Nouveaux Champs
```python
class Homework(models.Model):
    # ... champs existants ...
    
    # Nouveaux champs
    student = models.ForeignKey(
        CustomUser, 
        null=True, 
        blank=True, 
        limit_choices_to={"role": "student"},
        help_text="Étudiant spécifique (pour devoirs individuels)"
    )
    end_date = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Date et heure de fin de disponibilité"
    )
    is_individual = models.BooleanField(
        default=False, 
        help_text="Indique si le devoir est destiné à un étudiant spécifique"
    )
```

### Propriétés Calculées
```python
@property
def is_available(self):
    """Vérifie si le devoir est encore disponible"""
    if not self.end_date:
        return True
    return timezone.now() <= self.end_date

@property
def target_students(self):
    """Retourne la liste des étudiants ciblés"""
    if self.is_individual and self.student:
        return [self.student]
    else:
        # Tous les étudiants de la classe
        affectations = AffectationStudents.objects.filter(classroom=self.classes)
        return [aff.student for aff in affectations]
```

## API Endpoints

### 1. Créer un Devoir Individuel
```http
POST /api/homeworks/
Content-Type: application/json

{
    "name": "Devoir de rattrapage - Mathématiques",
    "description": "Devoir individuel pour étudiant malade",
    "form_link": "https://forms.google.com/example",
    "course": 1,
    "classes": 1,
    "level": 1,
    "student": 5,
    "end_date": "2024-01-20T23:59:59Z"
}
```

### 2. Créer un Devoir avec Date de Fin
```http
POST /api/homeworks/
Content-Type: application/json

{
    "name": "Devoir avec limite de temps",
    "description": "Ce devoir expire dans 2 heures",
    "form_link": "https://forms.google.com/example",
    "course": 1,
    "classes": 1,
    "level": 1,
    "end_date": "2024-01-15T14:00:00Z"
}
```

### 3. Récupérer les Devoirs Individuels
```http
GET /api/homeworks/individual/
```

### 4. Récupérer les Devoirs Disponibles
```http
GET /api/homeworks/available/
```

### 5. Récupérer les Devoirs Expirés
```http
GET /api/homeworks/expired/
```

### 6. Accès Sécurisé au Formulaire
```http
GET /api/homeworks/{id}/access_form/
```

**Réponse en cas de succès :**
```json
{
    "homework": {
        "id": 1,
        "name": "Devoir de Mathématiques",
        "description": "Exercices sur les équations",
        "is_available": true,
        "end_date": "2024-01-20T23:59:59Z"
    },
    "form_link": "https://forms.google.com/example",
    "access_granted": true
}
```

**Réponse en cas d'erreur :**
```json
{
    "error": "Ce devoir n'est plus disponible",
    "end_date": "15/01/2024 à 14:00"
}
```

## Gestion des Emails

### Modifications des Templates
Les emails utilisent maintenant des redirections sécurisées :

```html
<!-- Template email -->
<div class="homework-info">
    <h2>Nouveau devoir : {{ homework_name }}</h2>
    
    {% if is_individual %}
        <p class="individual-badge">📋 Devoir individuel</p>
    {% endif %}
    
    <p><strong>Description :</strong> {{ homework_description }}</p>
    
    {% if end_date %}
        <p><strong>Date limite :</strong> {{ end_date }}</p>
    {% endif %}
    
    <a href="{{ app_redirect_url }}" class="btn btn-primary">
        Accéder au devoir
    </a>
    
    <p class="security-note">
        💡 Important : Vous devez accéder au devoir via l'application 
        DialectosKoul pour des raisons de sécurité.
    </p>
</div>
```

### Contenu des Emails
- **Lien de redirection** : `http://localhost:5500/homework/{id}/`
- **Indication individuelle** : Badge pour les devoirs individuels
- **Date limite** : Affichage de la date de fin si définie
- **Message de sécurité** : Information sur l'accès sécurisé

## Sécurité et Contrôle d'Accès

### Vérifications d'Accès
1. **Authentification** : L'utilisateur doit être connecté
2. **Autorisation** : Vérification des permissions selon le rôle
3. **Ciblage** : Pour les devoirs individuels, vérification que l'étudiant est ciblé
4. **Disponibilité** : Vérification que le devoir n'est pas expiré
5. **Classe** : Pour les devoirs de classe, vérification de l'affectation

### Flux d'Accès Sécurisé
```
1. Étudiant clique sur le lien dans l'email
2. Redirection vers l'application : /homework/{id}/
3. L'application appelle l'API : GET /api/homeworks/{id}/access_form/
4. Vérification des permissions et disponibilité
5. Si autorisé : retour du lien du formulaire
6. Si refusé : message d'erreur approprié
```

## Tâches Celery

### Gestion des Devoirs Individuels
La tâche `send_scheduled_homeworks` a été mise à jour pour gérer les devoirs individuels :

```python
# Déterminer les étudiants ciblés
if homework.is_individual and homework.student:
    # Devoir individuel - cibler un seul étudiant
    target_students = [homework.student]
else:
    # Devoir de classe - cibler tous les étudiants de la classe
    affectations = AffectationStudents.objects.filter(classroom=homework.classes)
    target_students = [aff.student for aff in affectations]
```

### Gestion des Dates de Fin
- **Vérification automatique** : Les devoirs expirés ne sont pas envoyés
- **Logs détaillés** : Information sur les devoirs expirés dans les logs
- **Statistiques** : Comptage des devoirs disponibles vs expirés

## Cas d'Usage

### 1. Étudiant Malade
```python
# Créer un devoir de rattrapage
homework = Homework.objects.create(
    name="Devoir de rattrapage - Français",
    description="Devoir pour étudiant malade",
    form_link="https://forms.google.com/retake",
    course=french_course,
    classes=student_class,
    level=student_level,
    student=sick_student,  # Étudiant spécifique
    is_individual=True,
    end_date=timezone.now() + timedelta(days=7)  # 7 jours pour le rendre
)
```

### 2. Devoir avec Limite de Temps
```python
# Créer un devoir qui expire dans 2 heures
homework = Homework.objects.create(
    name="Quiz rapide - Histoire",
    description="Quiz de 30 minutes",
    form_link="https://forms.google.com/quick-quiz",
    course=history_course,
    classes=student_class,
    level=student_level,
    end_date=timezone.now() + timedelta(hours=2)  # Expire dans 2h
)
```

### 3. Devoir Planifié Individuel
```python
# Planifier un devoir pour un étudiant spécifique
homework = Homework.objects.create(
    name="Devoir de rattrapage planifié",
    description="Devoir programmé pour demain",
    form_link="https://forms.google.com/scheduled",
    course=math_course,
    classes=student_class,
    level=student_level,
    student=specific_student,
    is_individual=True,
    scheduled_date=timezone.now() + timedelta(days=1),  # Demain
    is_scheduled=True,
    end_date=timezone.now() + timedelta(days=3)  # 3 jours pour le rendre
)
```

## Tests

### Script de Test
Un script de test complet est fourni : `test_advanced_homework_features.py`

```bash
cd dialectoskoul
python test_advanced_homework_features.py
```

### Tests Inclus
1. **Devoirs individuels** : Création et vérification
2. **Dates de fin** : Devoirs avec et sans limite de temps
3. **Planification individuelle** : Devoirs planifiés pour un étudiant
4. **Statistiques** : Comptage des différents types de devoirs
5. **Tâches Celery** : Exécution des tâches planifiées

## Migration et Déploiement

### 1. Appliquer les Migrations
```bash
python manage.py makemigrations skoulApi
python manage.py migrate
```

### 2. Redémarrer les Services
```bash
# Redémarrer Celery Worker
celery -A dialectoskoul worker --loglevel=info

# Redémarrer Celery Beat
celery -A dialectoskoul beat --loglevel=info

# Redémarrer Django
python manage.py runserver
```

### 3. Vérifier le Fonctionnement
```bash
# Tester les nouvelles fonctionnalités
python test_advanced_homework_features.py

# Vérifier les logs
tail -f email_logs.log
```

## Monitoring et Logs

### Logs Importants
- **Création de devoirs** : Logs des devoirs individuels et avec dates de fin
- **Envoi d'emails** : Logs des emails avec redirections sécurisées
- **Accès aux formulaires** : Logs des tentatives d'accès
- **Erreurs de sécurité** : Logs des accès refusés

### Métriques à Surveiller
- Nombre de devoirs individuels créés
- Taux d'accès aux devoirs expirés (tentatives)
- Temps de réponse des redirections sécurisées
- Erreurs d'autorisation

## Évolutions Futures

### Fonctionnalités Possibles
1. **Notifications push** : Alertes pour les devoirs qui vont expirer
2. **Extensions de délai** : Possibilité de prolonger les dates de fin
3. **Devoirs récurrents** : Devoirs individuels récurrents
4. **Analytics** : Statistiques détaillées sur l'utilisation
5. **Templates personnalisés** : Emails personnalisés par type de devoir

### Améliorations Techniques
1. **Cache Redis** : Mise en cache des vérifications d'accès
2. **Rate limiting** : Limitation des tentatives d'accès
3. **Audit trail** : Traçabilité complète des accès
4. **API GraphQL** : Interface plus flexible pour les requêtes complexes
