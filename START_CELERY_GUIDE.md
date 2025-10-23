# Guide de Démarrage - Système d'Envoi Automatique d'Emails

## 🔴 PROBLÈME IDENTIFIÉ

**Les emails ne sont pas envoyés automatiquement car :**
1. ❌ Redis ne tourne pas
2. ❌ Celery Worker ne tourne pas
3. ❌ Celery Beat ne tourne pas

## ✅ SOLUTION : Démarrer les 4 Services

Pour que le système d'envoi automatique fonctionne, vous devez démarrer **4 services dans 4 terminaux différents** :

### Terminal 1 : Redis

**Windows** :
```powershell
# Si Redis n'est pas installé, téléchargez-le depuis :
# https://github.com/microsoftarchive/redis/releases

# Ensuite, démarrez Redis :
redis-server
```

**Linux/Mac** :
```bash
redis-server
```

**Résultat attendu** :
```
                _._                                                  
           _.-``__ ''-._                                             
      _.-``    `.  `_.  ''-._           Redis 6.2.6 (00000000/0) 64 bit
  .-`` .-```.  ```\/    _.,_ ''-._                                   
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
 |    `-._   `._    /     _.-'    |     
  `-._    `-._  `-./  _.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |                                  
  `-._    `-._`-.__.-'_.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |                                  
  `-._    `-._`-.__.-'_.-'    _.-'                                   
      `-._    `-.__.-'    _.-'                                       
          `-._        _.-'                                           
              `-.__.-'                                               

Ready to accept connections
```

---

### Terminal 2 : Celery Worker

```powershell
cd C:\Users\HP\Downloads\dialectoshool(1)\dialectoshool\dialectoskoul
celery -A dialectoskoul worker --loglevel=info --pool=solo
```

**Note Windows** : Ajoutez `--pool=solo` car Windows ne supporte pas le pool par défaut.

**Résultat attendu** :
```
-------------- celery@DESKTOP v5.x.x
---- **** ----- 
--- * ***  * -- Windows-10
-- * - **** --- 
- ** ---------- [config]
- ** ---------- .> app:         dialectoskoul:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 4
-- ******* ---- .> task events: OFF
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . skoulApi.tasks.send_homework_end_notifications
  . skoulApi.tasks.send_scheduled_homeworks
  
[2025-10-16 10:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-10-16 10:00:00,001: INFO/MainProcess] mingle: searching for neighbors
[2025-10-16 10:00:00,002: INFO/MainProcess] mingle: all alone
[2025-10-16 10:00:00,003: INFO/MainProcess] celery@DESKTOP ready.
```

---

### Terminal 3 : Celery Beat (Planificateur)

```powershell
cd C:\Users\HP\Downloads\dialectoshool(1)\dialectoshool\dialectoskoul
celery -A dialectoskoul beat --loglevel=info
```

**Résultat attendu** :
```
celery beat v5.x.x is starting.
__    -    ... __   -        _
LocalTime -> 2025-10-16 10:00:00
Configuration ->
    . broker -> redis://localhost:6379/0
    . loader -> celery.loaders.app.AppLoader
    . scheduler -> celery.beat.PersistentScheduler
    . db -> celerybeat-schedule
    . logfile -> [stderr]@%INFO
    . maxinterval -> 5.00 minutes (300s)

[2025-10-16 10:00:00,000: INFO/MainProcess] beat: Starting...
[2025-10-16 10:00:00,001: INFO/MainProcess] Scheduler: Sending due task send-scheduled-homeworks
[2025-10-16 10:02:00,001: INFO/MainProcess] Scheduler: Sending due task send-homework-end-notifications
```

---

### Terminal 4 : Django Server

```powershell
cd C:\Users\HP\Downloads\dialectoshool(1)\dialectoshool\dialectoskoul
python manage.py runserver
```

**Résultat attendu** :
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
October 16, 2025 - 10:00:00
Django version 3.2.4, using settings 'dialectoskoul.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## 🎯 Vérification que Tout Fonctionne

### 1. Vérifier Redis
Dans un nouveau terminal :
```powershell
redis-cli ping
# Devrait retourner: PONG
```

### 2. Vérifier Celery Worker
```powershell
celery -A dialectoskoul inspect active
# Devrait retourner la liste des tâches actives
```

### 3. Créer un Devoir de Test

**Via Python Shell** :
```powershell
cd dialectoskoul
python manage.py shell
```

```python
from skoulApi.models import Homework, Courses, Classes, LevelClass
from django.utils import timezone
from datetime import timedelta

# Récupérer les données
level = LevelClass.objects.first()
classe = Classes.objects.first()
course = Courses.objects.first()

# Créer un devoir planifié pour dans 1 minute
homework = Homework.objects.create(
    name="Test Envoi Automatique",
    description="Ce devoir devrait être envoyé automatiquement",
    form_link="https://forms.google.com/test",
    course=course,
    classes=classe,
    level=level,
    scheduled_date=timezone.now() + timedelta(minutes=1),
    is_scheduled=True,
    is_sent=False
)

print(f"Devoir créé - ID: {homework.id}")
print(f"Sera envoyé à: {homework.scheduled_date}")
```

**Résultat attendu** :
- Dans 1-2 minutes, vous devriez voir dans le terminal **Celery Worker** :
  ```
  [2025-10-16 10:01:00,000: INFO/MainProcess] Task send_scheduled_homeworks[...] received
  [2025-10-16 10:01:00,001: INFO/MainProcess] Traitement de 1 devoirs planifiés
  [2025-10-16 10:01:03,000: INFO/MainProcess] Devoir 'Test Envoi Automatique' envoyé avec succès
  ```

- Les emails seront envoyés aux étudiants de la classe

### 4. Vérifier les Logs

```powershell
# Logs d'email
type email_logs.log | findstr /i "success envoyé"

# Ou ouvrez le fichier email_logs.log
```

---

## 📊 Résumé de l'Architecture

```
┌─────────────┐
│   Django    │ ← Terminal 4 (python manage.py runserver)
│   Server    │   
└─────────────┘
      │
      │ Crée les devoirs avec scheduled_date
      ↓
┌─────────────┐
│    Redis    │ ← Terminal 1 (redis-server)
│   (Broker)  │   Message queue pour Celery
└─────────────┘
      ↑ ↓
┌─────────────┐
│ Celery Beat │ ← Terminal 3 (celery beat)
│(Planificateur)│  Exécute toutes les 1-2 minutes
└─────────────┘
      │
      │ Envoie la tâche "send_scheduled_homeworks"
      ↓
┌─────────────┐
│Celery Worker│ ← Terminal 2 (celery worker)
│ (Exécuteur) │   Exécute la tâche
└─────────────┘
      │
      │ Récupère les devoirs à envoyer
      │ Envoie les emails via Gmail SMTP
      ↓
┌─────────────┐
│  Étudiants  │
│   (Email)   │
└─────────────┘
```

---

## 🔧 Dépannage

### Problème 1 : "Error 10061 connecting to localhost:6379"
**Cause** : Redis ne tourne pas  
**Solution** : Démarrer Redis dans Terminal 1

### Problème 2 : "No module named 'celery'"
**Cause** : Celery n'est pas installé  
**Solution** : 
```powershell
pip install celery redis
```

### Problème 3 : "Unable to load celery application"
**Cause** : Mauvais répertoire  
**Solution** : Assurez-vous d'être dans `dialectoskoul/` (pas `dialectoshool(1)/`)

### Problème 4 : Les tâches ne s'exécutent pas
**Cause** : Celery Beat ne tourne pas ou est dans le mauvais répertoire  
**Solution** : Vérifier Terminal 3

### Problème 5 : Emails non reçus
**Vérifications** :
1. Configuration email dans `settings.py`
2. Étudiants ont des emails valides
3. Logs dans `email_logs.log`
4. Vérifier spams/courrier indésirable

---

## 💡 Commandes Rapides

### Tout Démarrer (4 terminaux)

**Terminal 1** :
```powershell
redis-server
```

**Terminal 2** :
```powershell
cd C:\Users\HP\Downloads\dialectoshool(1)\dialectoshool\dialectoskoul
celery -A dialectoskoul worker --loglevel=info --pool=solo
```

**Terminal 3** :
```powershell
cd C:\Users\HP\Downloads\dialectoshool(1)\dialectoshool\dialectoskoul
celery -A dialectoskoul beat --loglevel=info
```

**Terminal 4** :
```powershell
cd C:\Users\HP\Downloads\dialectoshool(1)\dialectoshool\dialectoskoul
python manage.py runserver
```

### Tout Arrêter
Dans chaque terminal, appuyez sur `Ctrl+C`

---

## ✅ Checklist de Vérification

- [ ] Redis tourne (Terminal 1 affiche "Ready to accept connections")
- [ ] Celery Worker tourne (Terminal 2 affiche "celery@DESKTOP ready")
- [ ] Celery Beat tourne (Terminal 3 affiche "beat: Starting...")
- [ ] Django tourne (Terminal 4 affiche "Starting development server")
- [ ] `redis-cli ping` retourne PONG
- [ ] `celery -A dialectoskoul inspect active` ne retourne pas d'erreur
- [ ] Devoirs planifiés existent dans la base de données
- [ ] Étudiants ont des emails valides

---

## 📚 Documentation Liée

- `HOMEWORK_SCHEDULING_README.md` - Système de planification
- `HOMEWORK_END_NOTIFICATION_README.md` - Notifications de dépublication
- `ADVANCED_HOMEWORK_FEATURES_README.md` - Fonctionnalités avancées
- `diagnose_celery.py` - Script de diagnostic

---

## 🎉 Une Fois Configuré

Après avoir démarré les 4 services, le système fonctionne automatiquement :

1. **Devoirs planifiés** : Envoyés automatiquement quand `scheduled_date` arrive
2. **Notifications de fin** : Envoyées automatiquement quand `end_date` arrive
3. **Logs automatiques** : Tous les envois sont enregistrés dans `email_logs.log`
4. **Pas d'intervention manuelle** : Tout est automatique !

Laissez simplement les 4 terminaux ouverts pendant que vous travaillez sur le projet.

