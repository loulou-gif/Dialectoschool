# Système de Planification des Devoirs

## Vue d'ensemble

Le système de planification des devoirs permet aux administrateurs de programmer l'envoi de devoirs à une date et heure spécifiques. Les emails seront automatiquement envoyés aux étudiants quand la date planifiée sera atteinte.

## Fonctionnalités

### 1. Planification des Devoirs
- **Envoi immédiat** : Les devoirs sont envoyés immédiatement aux étudiants
- **Envoi planifié** : Les devoirs sont programmés pour être envoyés à une date/heure spécifique
- **Gestion des statuts** : Suivi de l'état d'envoi des devoirs

### 2. Nouveaux Champs du Modèle Homework
- `scheduled_date` : Date et heure d'envoi planifiée
- `is_scheduled` : Indique si le devoir est planifié
- `is_sent` : Indique si le devoir a été envoyé

### 3. Actions API Disponibles

#### Créer un Devoir Planifié
```http
POST /api/homeworks/
Content-Type: application/json

{
    "name": "Devoir de Mathématiques",
    "description": "Exercices sur les équations",
    "form_link": "https://forms.google.com/example",
    "course": 1,
    "classes": 1,
    "level": 1,
    "scheduled_date": "2024-01-15T10:00:00Z",
    "is_scheduled": true
}
```

#### Envoyer un Devoir Immédiatement
```http
POST /api/homeworks/{id}/send_now/
```

#### Annuler la Planification
```http
POST /api/homeworks/{id}/cancel_schedule/
```

#### Récupérer les Devoirs Planifiés
```http
GET /api/homeworks/scheduled/
```

## Configuration Technique

### 1. Celery et Redis
Le système utilise Celery avec Redis comme broker pour gérer les tâches asynchrones.

#### Installation des Dépendances
```bash
pip install celery redis django-celery-beat
```

#### Configuration dans settings.py
```python
# Configuration Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

### 2. Démarrage des Services

#### Démarrer Redis
```bash
redis-server
```

#### Démarrer Celery Worker
```bash
cd dialectoskoul
celery -A dialectoskoul worker --loglevel=info
```

#### Démarrer Celery Beat (Planificateur)
```bash
cd dialectoskoul
celery -A dialectoskoul beat --loglevel=info
```

#### Démarrer Django
```bash
cd dialectoskoul
python manage.py runserver
```

### 3. Tâches Celery

#### Tâche Principale : `send_scheduled_homeworks`
- Exécutée toutes les minutes
- Vérifie les devoirs planifiés dont la date est atteinte
- Envoie les emails aux étudiants
- Met à jour le statut des devoirs

#### Tâche Optionnelle : `send_homework_reminder`
- Pour envoyer des rappels de devoirs

## Utilisation

### 1. Créer un Devoir Planifié

#### Via l'API REST
```python
import requests
from datetime import datetime, timedelta

# Date de planification (dans 1 heure)
scheduled_time = datetime.now() + timedelta(hours=1)

data = {
    "name": "Devoir de Français",
    "description": "Rédaction sur un sujet libre",
    "form_link": "https://forms.google.com/francais",
    "course": 1,
    "classes": 1,
    "level": 1,
    "scheduled_date": scheduled_time.isoformat(),
    "is_scheduled": True
}

response = requests.post('http://localhost:8000/api/homeworks/', json=data)
print(response.json())
```

#### Via l'Interface Django Admin
1. Aller dans l'interface d'administration Django
2. Sélectionner "Homeworks"
3. Créer un nouveau devoir
4. Remplir les champs obligatoires
5. Définir `scheduled_date` et cocher `is_scheduled`
6. Sauvegarder

### 2. Gérer les Devoirs Planifiés

#### Voir tous les devoirs planifiés
```python
response = requests.get('http://localhost:8000/api/homeworks/scheduled/')
scheduled_homeworks = response.json()
print(f"Nombre de devoirs planifiés: {scheduled_homeworks['count']}")
```

#### Envoyer immédiatement un devoir planifié
```python
homework_id = 1
response = requests.post(f'http://localhost:8000/api/homeworks/{homework_id}/send_now/')
print(response.json())
```

#### Annuler la planification
```python
homework_id = 1
response = requests.post(f'http://localhost:8000/api/homeworks/{homework_id}/cancel_schedule/')
print(response.json())
```

## Test du Système

### Script de Test
Un script de test est fourni pour vérifier le fonctionnement :

```bash
cd dialectoskoul
python test_homework_scheduling.py
```

Ce script :
1. Crée des devoirs de test
2. Teste la planification
3. Exécute la tâche Celery
4. Vérifie les résultats
5. Nettoie les données de test

### Vérification Manuelle

#### 1. Vérifier que Celery fonctionne
```bash
# Dans un terminal
celery -A dialectoskoul inspect active
```

#### 2. Vérifier les logs
```bash
# Les logs sont dans email_logs.log
tail -f email_logs.log
```

#### 3. Vérifier la base de données
```python
from skoulApi.models import Homework

# Voir tous les devoirs planifiés
scheduled = Homework.objects.filter(is_scheduled=True, is_sent=False)
for hw in scheduled:
    print(f"{hw.name} - {hw.scheduled_date}")
```

## Dépannage

### Problèmes Courants

#### 1. Redis n'est pas démarré
```
Error: [Errno 111] Connection refused
```
**Solution** : Démarrer Redis avec `redis-server`

#### 2. Celery Worker n'est pas démarré
```
Task not found: skoulApi.tasks.send_scheduled_homeworks
```
**Solution** : Démarrer le worker avec `celery -A dialectoskoul worker --loglevel=info`

#### 3. Les emails ne sont pas envoyés
**Vérifications** :
- Configuration email dans settings.py
- Logs dans email_logs.log
- Statut des devoirs dans la base de données

#### 4. Les tâches ne s'exécutent pas
**Vérifications** :
- Celery Beat est démarré
- Configuration de la planification dans celery.py
- Logs Celery

### Logs et Monitoring

#### Logs Celery
```bash
celery -A dialectoskoul events
```

#### Logs Email
```bash
tail -f email_logs.log
```

#### Monitoring Redis
```bash
redis-cli monitor
```

## Sécurité et Bonnes Pratiques

### 1. Sécurité
- Les emails contiennent des liens sécurisés
- Validation des dates de planification
- Gestion des erreurs d'envoi

### 2. Performance
- Tâches asynchrones pour éviter les blocages
- Gestion des erreurs sans interruption du service
- Logs détaillés pour le debugging

### 3. Maintenance
- Nettoyage régulier des logs
- Monitoring des tâches Celery
- Sauvegarde de la base de données

## Évolutions Futures

### Fonctionnalités Possibles
1. **Rappels automatiques** : Envoyer des rappels avant la date limite
2. **Planification récurrente** : Devoirs récurrents (hebdomadaires, mensuels)
3. **Templates d'emails** : Personnalisation des emails
4. **Statistiques** : Tableaux de bord pour les administrateurs
5. **Notifications push** : Intégration avec des services de notification

### Améliorations Techniques
1. **Interface web** : Interface graphique pour la planification
2. **API avancée** : Endpoints pour la gestion en masse
3. **Monitoring** : Dashboard de monitoring des tâches
4. **Tests automatisés** : Suite de tests complète
