# 🔍 Diagnostic Final - Système d'Envoi d'Emails

## ❌ PROBLÈME IDENTIFIÉ

Vos logs montrent que **les emails ne sont pas envoyés automatiquement** pour :
- ✅ La publication programmée des devoirs
- ✅ La dépublication des devoirs

### Cause Principale
**Celery Worker et Celery Beat ne tournent pas !**

Les logs `email_logs.log` montrent uniquement des tests manuels, aucune exécution automatique par Celery.

## ✅ SOLUTION IMMÉDIATE

### Option 1 : Script Automatique (Windows)

Double-cliquez sur :
```
start_all_services.bat
```

Ce script ouvrira automatiquement 4 terminaux :
1. Redis Server
2. Celery Worker  
3. Celery Beat
4. Django Server

### Option 2 : Démarrage Manuel

Ouvrez **4 terminaux PowerShell** et exécutez dans chacun :

**Terminal 1 - Redis** :
```powershell
redis-server
```

**Terminal 2 - Celery Worker** :
```powershell
cd C:\Users\HP\Downloads\dialectoshool(1)\dialectoshool\dialectoskoul
celery -A dialectoskoul worker --loglevel=info --pool=solo
```

**Terminal 3 - Celery Beat** :
```powershell
cd C:\Users\HP\Downloads\dialectoshool(1)\dialectoshool\dialectoskoul
celery -A dialectoskoul beat --loglevel=info
```

**Terminal 4 - Django** :
```powershell
cd C:\Users\HP\Downloads\dialectoshool(1)\dialectoshool\dialectoskoul
python manage.py runserver
```

## 🧪 VÉRIFICATION

### 1. Vérifier Redis
```powershell
redis-cli ping
# Doit retourner: PONG
```

### 2. Vérifier Celery
```powershell
celery -A dialectoskoul inspect active
# Doit afficher les tâches sans erreur
```

### 3. Test Complet

Exécutez le script de diagnostic :
```powershell
cd dialectoskoul
python diagnose_celery.py
```

Le script va :
- ✅ Vérifier Redis
- ✅ Vérifier la configuration Celery
- ✅ Lister les devoirs à envoyer
- ✅ Créer un devoir de test (optionnel)

## 📊 CE QUI VA SE PASSER APRÈS

### Envoi Automatique des Devoirs Programmés

**Tâche** : `send_scheduled_homeworks`  
**Fréquence** : Toutes les **60 secondes** (1 minute)  
**Action** : Envoie les emails pour tous les devoirs où :
```
is_scheduled = True
is_sent = False  
scheduled_date <= maintenant
```

**Logs attendus dans Terminal 2 (Celery Worker)** :
```
[2025-10-16 10:01:00] Task send_scheduled_homeworks received
[2025-10-16 10:01:00] INFO Traitement de 1 devoirs planifiés
[2025-10-16 10:01:00] INFO Préparation de l'envoi d'emails pour le devoir ...
[2025-10-16 10:01:03] INFO Email de devoir envoyé avec succès à ...
[2025-10-16 10:01:03] INFO Emails de devoir envoyés : 2 succès, 0 échecs
[2025-10-16 10:01:03] Task send_scheduled_homeworks succeeded
```

### Envoi Automatique des Notifications de Dépublication

**Tâche** : `send_homework_end_notifications`  
**Fréquence** : Toutes les **120 secondes** (2 minutes)  
**Action** : Envoie les emails pour tous les devoirs où :
```
end_date != null
end_date <= maintenant
end_notification_sent = False
```

**Logs attendus dans Terminal 2 (Celery Worker)** :
```
[2025-10-16 10:02:00] Task send_homework_end_notifications received
[2025-10-16 10:02:00] INFO Traitement de 1 notifications de dépublication
[2025-10-16 10:02:00] INFO Envoi de notifications de dépublication pour le devoir: ...
[2025-10-16 10:02:03] INFO Email de dépublication envoyé avec succès à ...
[2025-10-16 10:02:03] Task send_homework_end_notifications succeeded
```

## 📝 EXEMPLE COMPLET

### Scénario : Créer un Devoir Programmé

```python
# Via Python Shell
python manage.py shell

from skoulApi.models import Homework, Courses, Classes, LevelClass
from django.utils import timezone
from datetime import timedelta

level = LevelClass.objects.first()
classe = Classes.objects.first()
course = Courses.objects.first()

# Devoir programmé pour dans 2 minutes avec fin dans 1 heure
homework = Homework.objects.create(
    name="Devoir de Test Automatique",
    description="Test du système d'envoi automatique",
    form_link="https://forms.google.com/test",
    course=course,
    classes=classe,
    level=level,
    scheduled_date=timezone.now() + timedelta(minutes=2),  # Dans 2 min
    end_date=timezone.now() + timedelta(hours=1),  # Expire dans 1h
    is_scheduled=True,
    is_sent=False
)

print(f"Devoir créé - ID: {homework.id}")
print(f"Envoi programmé à: {homework.scheduled_date}")
print(f"Expire à: {homework.end_date}")
```

**Résultat attendu** :

1. **Dans 2 minutes** : 
   - Email "Nouveau devoir : Devoir de Test Automatique" envoyé aux étudiants
   - `is_sent = True` automatiquement

2. **Dans 1 heure** :
   - Email "Fin de disponibilité : Devoir de Test Automatique" envoyé
   - `end_notification_sent = True` automatiquement
   - Devoir masqué pour les étudiants
   - Devoir visible pour les professeurs

## 📈 MONITORING

### Voir les Logs en Temps Réel

**Logs Celery (Terminal 2 et 3)** :
- Les logs s'affichent directement dans les terminaux

**Logs Email** :
```powershell
# Windows
type email_logs.log

# Ou utilisez un éditeur pour suivre en temps réel
notepad email_logs.log
```

**Logs Django** :
- Terminal 4 affiche les requêtes HTTP

### Statistiques

```python
# Via Python Shell
from skoulApi.models import Homework
from django.utils import timezone

# Devoirs programmés en attente
pending = Homework.objects.filter(is_scheduled=True, is_sent=False)
print(f"En attente: {pending.count()}")

# Devoirs envoyés
sent = Homework.objects.filter(is_sent=True)
print(f"Envoyés: {sent.count()}")

# Devoirs expirés à notifier
now = timezone.now()
to_notify = Homework.objects.filter(
    end_date__lte=now,
    end_notification_sent=False
)
print(f"À notifier: {to_notify.count()}")
```

## ⚠️ POINTS IMPORTANTS

### 1. Les 4 Services DOIVENT Tourner
- Si l'un des services s'arrête, l'envoi automatique ne fonctionne pas
- Laissez les 4 terminaux ouverts

### 2. Délai Maximum
- **Devoirs programmés** : Envoyés dans les 60 secondes après `scheduled_date`
- **Notifications de fin** : Envoyées dans les 120 secondes après `end_date`

### 3. Pas de Doublons
- `is_sent` évite le renvoi des devoirs programmés
- `end_notification_sent` évite le renvoi des notifications de fin

### 4. Frontend
- Le frontend peut appeler `/api/send-homework-notifications/` pour forcer l'envoi manuel
- Mais l'envoi automatique fonctionne sans intervention

## 🐛 DÉPANNAGE

### "Redis connection refused"
**Problème** : Redis ne tourne pas  
**Solution** : Démarrer `redis-server` dans Terminal 1

### "No module named 'celery'"
**Problème** : Celery non installé  
**Solution** : `pip install celery redis`

### Aucun log dans Celery Worker
**Problème** : Celery Beat ne tourne pas  
**Solution** : Vérifier Terminal 3

### Emails non reçus mais logs OK
**Problème** : Configuration email  
**Solution** : 
1. Vérifier `settings.py` → `EMAIL_HOST_PASSWORD`
2. Vérifier emails étudiants
3. Vérifier spams

## 📚 DOCUMENTATION

Tous les détails sont dans :
- `START_CELERY_GUIDE.md` - Guide complet de démarrage
- `HOMEWORK_SCHEDULING_README.md` - Système de planification
- `HOMEWORK_END_NOTIFICATION_README.md` - Notifications de fin
- `diagnose_celery.py` - Script de diagnostic

## 🎯 CHECKLIST RAPIDE

- [ ] Redis tourne
- [ ] Celery Worker tourne
- [ ] Celery Beat tourne  
- [ ] Django tourne
- [ ] `redis-cli ping` → PONG
- [ ] Devoirs programmés créés
- [ ] Attendre 1-2 minutes
- [ ] Vérifier logs Celery Worker
- [ ] Vérifier `email_logs.log`
- [ ] Vérifier emails reçus

## ✅ RÉSUMÉ

**Actuellement** : ❌ Aucun service Celery ne tourne  
**À faire** : ✅ Démarrer les 4 services (utilisez `start_all_services.bat`)  
**Résultat** : 🎉 Emails envoyés automatiquement !

---

**Besoin d'aide ?** Exécutez `python diagnose_celery.py` pour un diagnostic complet.

