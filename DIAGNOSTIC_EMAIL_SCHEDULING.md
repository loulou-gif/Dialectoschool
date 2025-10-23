# Diagnostic - Envoi d'Emails pour Devoirs Programmés

## Problème Identifié
L'envoi d'emails pour les devoirs programmés ne fonctionne pas.

## Corrections Apportées

### 1. Endpoint API créé
✅ **Créé** : `POST /api/send-homework-notifications/`
- Permet au frontend de déclencher manuellement l'envoi
- Appelle la tâche Celery `send_scheduled_homeworks()`

### 2. Service d'envoi corrigé
✅ **Modifié** : `send_homework_assignment_email()` dans `services.py`
- Gère maintenant les devoirs individuels
- Cible correctement les étudiants selon le type de devoir

## Points à Vérifier

### 1. Configuration Email
Vérifiez dans `settings.py` :
```python
EMAIL_BACKEND = "skoulApi.email_backend.CustomEmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "konankanjulius10@gmail.com"
EMAIL_HOST_PASSWORD = "bsrm dlyd eevr nuku"
```

### 2. Services Celery
Assurez-vous que ces services tournent :

#### Redis
```bash
redis-server
```

#### Celery Worker
```bash
cd dialectoskoul
celery -A dialectoskoul worker --loglevel=info
```

#### Celery Beat
```bash
cd dialectoskoul
celery -A dialectoskoul beat --loglevel=info
```

### 3. Tester l'Envoi Manuel

#### Via Python Shell
```python
python manage.py shell

from skoulApi.models import Homework
from skoulApi.tasks import send_scheduled_homeworks
from django.utils import timezone

# Voir les devoirs à envoyer
homeworks = Homework.objects.filter(
    is_scheduled=True,
    is_sent=False,
    scheduled_date__lte=timezone.now()
)
print(f"Devoirs à envoyer: {homeworks.count()}")

# Tester l'envoi
result = send_scheduled_homeworks()
print(result)
```

#### Via API
```bash
curl -X POST http://localhost:8000/api/send-homework-notifications/
```

### 4. Créer un Devoir de Test

```python
python manage.py shell

from skoulApi.models import Homework, Courses, Classes, LevelClass
from django.utils import timezone
from datetime import timedelta

# Récupérer les données
level = LevelClass.objects.first()
classe = Classes.objects.first()
course = Courses.objects.first()

# Créer un devoir programmé pour maintenant
homework = Homework.objects.create(
    name="Test Email Programmé",
    description="Test d'envoi d'email",
    form_link="https://forms.google.com/test",
    course=course,
    classes=classe,
    level=level,
    scheduled_date=timezone.now() - timedelta(minutes=1),
    is_scheduled=True,
    is_sent=False
)

print(f"Devoir créé - ID: {homework.id}")

# Tester l'envoi
from skoulApi.tasks import send_scheduled_homeworks
result = send_scheduled_homeworks()
print(result)

# Vérifier
homework.refresh_from_db()
print(f"Envoyé: {homework.is_sent}")
```

## Vérifications des Logs

### 1. Logs Email
```bash
tail -f email_logs.log
```

### 2. Logs Celery
Vérifiez la sortie du terminal où Celery Worker tourne.

### 3. Logs Django
Vérifiez la sortie du serveur Django.

## Causes Possibles du Problème

### 1. Celery ne tourne pas
**Symptôme** : Les devoirs ne sont jamais envoyés automatiquement
**Solution** : Démarrer Celery Worker et Beat

### 2. Redis ne tourne pas
**Symptôme** : Erreur de connexion
**Solution** : Démarrer Redis

### 3. Configuration email incorrecte
**Symptôme** : Erreur lors de l'envoi
**Solution** : Vérifier les identifiants email

### 4. Aucun étudiant dans la classe
**Symptôme** : Aucun email envoyé
**Solution** : Vérifier les affectations étudiants

### 5. Date programmée dans le futur
**Symptôme** : Devoir non envoyé
**Solution** : Vérifier que `scheduled_date <= now()`

## Tests à Effectuer

### Test 1 : Envoi Immédiat
```python
from skoulApi.models import Homework
from skoulApi.services import send_homework_assignment_email

homework = Homework.objects.get(id=X)  # Remplacer X
success = send_homework_assignment_email(homework)
print(f"Succès: {success}")
```

### Test 2 : Tâche Celery
```python
from skoulApi.tasks import send_scheduled_homeworks
result = send_scheduled_homeworks()
print(result)
```

### Test 3 : Endpoint API
```javascript
// Depuis le frontend
fetch('/api/send-homework-notifications/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Commandes Utiles

### Vérifier Celery
```bash
# Voir les tâches actives
celery -A dialectoskoul inspect active

# Voir les tâches planifiées
celery -A dialectoskoul inspect scheduled

# Voir les workers
celery -A dialectoskoul inspect stats
```

### Vérifier Redis
```bash
redis-cli ping
# Devrait retourner: PONG
```

### Vérifier les Devoirs Programmés
```python
python manage.py shell

from skoulApi.models import Homework
from django.utils import timezone

# Devoirs à envoyer maintenant
to_send = Homework.objects.filter(
    is_scheduled=True,
    is_sent=False,
    scheduled_date__lte=timezone.now()
)

for hw in to_send:
    print(f"ID: {hw.id}, Nom: {hw.name}, Date: {hw.scheduled_date}")
```

## Solution Rapide

Si rien ne fonctionne, essayez cette séquence :

1. **Redémarrer tous les services**
```bash
# Terminal 1 - Redis
redis-server

# Terminal 2 - Celery Worker
cd dialectoskoul
celery -A dialectoskoul worker --loglevel=info

# Terminal 3 - Celery Beat
cd dialectoskoul
celery -A dialectoskoul beat --loglevel=info

# Terminal 4 - Django
cd dialectoskoul
python manage.py runserver
```

2. **Créer un devoir de test**
```python
# Via manage.py shell
# ... (voir code ci-dessus)
```

3. **Appeler l'endpoint manuellement**
```bash
curl -X POST http://localhost:8000/api/send-homework-notifications/
```

## Support

Si le problème persiste, vérifiez :
1. Les logs dans `email_logs.log`
2. La sortie du terminal Celery Worker
3. Les erreurs dans la console Django
4. La configuration email dans `settings.py`

