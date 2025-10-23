# Système de Notification de Dépublication des Devoirs

## Vue d'ensemble

Le système envoie automatiquement des emails aux étudiants lorsqu'un devoir atteint sa date de dépublication (`end_date`). Les étudiants sont notifiés que le devoir n'est plus accessible.

## Fonctionnalités Implémentées

### 1. ✅ Filtrage Automatique pour les Étudiants
- Les devoirs expirés sont automatiquement masqués dans l'API pour les étudiants
- Les professeurs et admins voient tous les devoirs (actifs + expirés)

### 2. ✅ Notifications Automatiques
- Emails envoyés automatiquement quand `end_date` est atteinte
- Gestion des devoirs de classe et devoirs individuels
- Évite les doublons avec le champ `end_notification_sent`

### 3. ✅ Tâche Celery Périodique
- Exécution automatique toutes les 2 minutes
- Vérifie les devoirs expirés non notifiés
- Envoie les emails et marque comme notifié

## Modifications Apportées

### 1. Modèle `Homework`

**Nouveau champ ajouté** :
```python
end_notification_sent = models.BooleanField(
    default=False,
    help_text="Indique si la notification de dépublication a été envoyée"
)
```

### 2. Vue `HomeworkViewSet`

**Filtre pour les étudiants** :
```python
def get_queryset(self):
    # ...
    elif user.role == 'student':
        # Filtrer les devoirs expirés
        queryset = queryset.filter(
            Q(end_date__isnull=True) | Q(end_date__gt=now)
        )
```

### 3. Service Email

**Nouvelle fonction** : `send_homework_end_notification_email(homework)`
- Envoie un email aux étudiants concernés
- Gère les devoirs individuels et de classe
- Email informatif sur la fin de disponibilité

### 4. Tâche Celery

**Nouvelle tâche** : `send_homework_end_notifications()`
- Trouve les devoirs expirés non notifiés
- Envoie les notifications
- Marque comme notifié

### 5. Configuration Celery Beat

```python
'send-homework-end-notifications': {
    'task': 'skoulApi.tasks.send_homework_end_notifications',
    'schedule': 120.0,  # Exécuter toutes les 2 minutes
},
```

## Fonctionnement

### Flux Automatique

```
1. Celery Beat s'exécute toutes les 2 minutes
   ↓
2. Appelle la tâche send_homework_end_notifications()
   ↓
3. Recherche les devoirs avec:
   - end_date <= maintenant
   - end_notification_sent = False
   ↓
4. Pour chaque devoir trouvé:
   - Envoie un email aux étudiants concernés
   - Marque end_notification_sent = True
```

### Comportement API

#### Pour les ÉTUDIANTS
```
GET /api/homework/
→ Retourne uniquement les devoirs disponibles (end_date > maintenant OU end_date = null)
```

#### Pour les PROFESSEURS/ADMINS
```
GET /api/homework/
→ Retourne TOUS les devoirs (actifs + expirés)
```

## Contenu de l'Email

Les étudiants reçoivent un email avec :
- Titre : "Fin de disponibilité : [Nom du devoir]"
- Date de fin du devoir
- Détails du devoir (cours, classe, niveau)
- Message informatif sur la possibilité de contacter le professeur

**Exemple d'email** :
```
Fin de disponibilité du devoir

Bonjour [Nom de l'étudiant],

Le devoir "Devoir de Mathématiques" n'est plus disponible depuis le 15/01/2024 à 23:59.

📚 Détails du devoir
📝 Titre : Devoir de Mathématiques
📖 Cours : Mathématiques
🏫 Classe : Cohorte 001
📊 Niveau : Débutant
⏰ Date de fin : 15/01/2024 à 23:59

📋 Description
[Description du devoir]

ℹ️ Ce devoir n'est plus accessible. Si vous n'avez pas eu le temps de le terminer 
et que vous avez une raison valable (maladie, problème technique, etc.), 
veuillez contacter votre professeur.

Cordialement,
L'équipe DialectosKoul
```

## Migration

### Commandes Exécutées
```bash
python manage.py makemigrations
python manage.py migrate
```

**Migration créée** : `0007_homework_end_notification_sent`

## Test du Système

### Script de Test
Un script complet est fourni : `test_end_notification.py`

```bash
cd dialectoskoul
python test_end_notification.py
```

### Tests Effectués
1. ✅ Création de devoir expiré
2. ✅ Création de devoir individuel expiré
3. ✅ Création de devoir futur (non expiré)
4. ✅ Envoi direct de notification
5. ✅ Exécution de la tâche Celery
6. ✅ Vérification du marquage des notifications
7. ✅ Statistiques

### Résultats des Tests
```
📊 État après exécution:
   - Devoir individuel notification envoyée: True ✅
   - Devoir futur notification envoyée: False ✅

📈 Statistiques:
   - Total devoirs expirés: 3
   - Total notifications envoyées: 3
```

## Utilisation

### 1. Créer un Devoir avec Date de Fin

```python
# Via l'API
POST /api/homework/
{
    "name": "Devoir de Français",
    "description": "Rédaction",
    "form_link": "https://forms.google.com/example",
    "course": 1,
    "classes": 1,
    "level": 1,
    "end_date": "2024-01-20T23:59:59Z"
}
```

### 2. Le Système Gère Automatiquement

- **Avant end_date** : Devoir visible pour les étudiants
- **À end_date** : 
  - Email envoyé automatiquement
  - Devoir masqué pour les étudiants
  - Devoir toujours visible pour les professeurs

### 3. Vérifier les Notifications

```python
# Via Python Shell
from skoulApi.models import Homework

# Devoirs expirés notifiés
notified = Homework.objects.filter(
    end_date__isnull=False,
    end_notification_sent=True
)

# Devoirs expirés non notifiés
pending = Homework.objects.filter(
    end_date__isnull=False,
    end_date__lte=timezone.now(),
    end_notification_sent=False
)
```

## Démarrage des Services

Pour que le système fonctionne, vous devez démarrer :

### 1. Redis
```bash
redis-server
```

### 2. Celery Worker
```bash
cd dialectoskoul
celery -A dialectoskoul worker --loglevel=info
```

### 3. Celery Beat
```bash
cd dialectoskoul
celery -A dialectoskoul beat --loglevel=info
```

### 4. Django
```bash
cd dialectoskoul
python manage.py runserver
```

## Monitoring

### Logs
```bash
# Logs d'email
tail -f email_logs.log

# Logs Celery (dans le terminal où Celery Worker tourne)
```

### Vérifier les Tâches Celery
```bash
# Voir les tâches actives
celery -A dialectoskoul inspect active

# Voir les tâches planifiées
celery -A dialectoskoul inspect scheduled
```

## Points Importants

### 1. Fréquence de Vérification
- La tâche s'exécute toutes les **2 minutes**
- Les notifications peuvent avoir jusqu'à 2 minutes de retard

### 2. Éviter les Doublons
- Le champ `end_notification_sent` évite l'envoi multiple
- Une fois envoyé, le devoir ne reçoit plus de notification

### 3. Devoirs Sans Date de Fin
- Si `end_date` est `null`, le devoir reste toujours disponible
- Aucune notification de dépublication n'est envoyée

### 4. Devoirs Individuels
- Les notifications sont envoyées uniquement à l'étudiant concerné
- Les devoirs de classe notifient tous les étudiants de la classe

## Dépannage

### Problème : Aucune Notification Envoyée

**Vérifications** :
1. Celery Beat tourne-t-il ?
2. Le devoir a-t-il une `end_date` ?
3. La `end_date` est-elle dépassée ?
4. `end_notification_sent` est-il à False ?

### Problème : Emails Non Reçus

**Vérifications** :
1. Configuration email dans `settings.py`
2. Logs dans `email_logs.log`
3. Adresses email des étudiants valides
4. Étudiants affectés à la classe

### Problème : Devoirs Expirés Visibles pour Étudiants

**Cause** : Cache frontend ou filtre non appliqué

**Solution** : 
- Vider le cache frontend
- Vérifier que l'utilisateur est bien `role=student`
- Vérifier le filtre dans `get_queryset()`

## Exemple Complet

### Scénario : Devoir avec Limite de 24h

```python
from django.utils import timezone
from datetime import timedelta
from skoulApi.models import Homework

# Créer un devoir qui expire dans 24h
homework = Homework.objects.create(
    name="Quiz Rapide - Histoire",
    description="Quiz de 30 minutes à faire dans les 24h",
    form_link="https://forms.google.com/quiz",
    course=course,
    classes=classe,
    level=level,
    scheduled_date=timezone.now(),  # Envoi immédiat
    end_date=timezone.now() + timedelta(hours=24),  # Expire dans 24h
    is_scheduled=False
)

# Résultat :
# - Email envoyé immédiatement aux étudiants
# - Devoir disponible pendant 24h
# - Après 24h : notification automatique de fin
# - Devoir masqué pour les étudiants
```

## Statistiques

### Requêtes Utiles

```python
from django.utils import timezone
from skoulApi.models import Homework

# Total devoirs avec date de fin
with_end_date = Homework.objects.filter(end_date__isnull=False).count()

# Devoirs actuellement disponibles
available = Homework.objects.filter(
    Q(end_date__isnull=True) | Q(end_date__gt=timezone.now())
).count()

# Devoirs expirés
expired = Homework.objects.filter(
    end_date__isnull=False,
    end_date__lte=timezone.now()
).count()

# Notifications envoyées
notified = Homework.objects.filter(end_notification_sent=True).count()

print(f"Avec date de fin: {with_end_date}")
print(f"Disponibles: {available}")
print(f"Expirés: {expired}")
print(f"Notifications envoyées: {notified}")
```

## Évolutions Futures

### Fonctionnalités Possibles
1. **Rappels avant expiration** : Email 24h/1h avant la fin
2. **Extensions de délai** : Permettre au professeur de prolonger
3. **Notifications personnalisées** : Templates différents selon le type
4. **Dashboard professeur** : Statistiques sur les devoirs expirés
5. **Historique des notifications** : Traçabilité complète

