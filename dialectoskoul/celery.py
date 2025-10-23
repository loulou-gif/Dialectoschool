import os
from celery import Celery
from django.conf import settings

# Configuration de l'environnement Django pour Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dialectoskoul.settings')

app = Celery('dialectoskoul')

# Configuration Celery avec les paramètres Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découverte automatique des tâches dans les applications Django
app.autodiscover_tasks()

# Configuration des tâches périodiques (Celery Beat)
app.conf.beat_schedule = {
    'send-scheduled-homeworks': {
        'task': 'skoulApi.tasks.send_scheduled_homeworks',
        'schedule': 60.0,  # Exécuter toutes les minutes
    },
    'send-homework-end-notifications': {
        'task': 'skoulApi.tasks.send_homework_end_notifications',
        'schedule': 120.0,  # Exécuter toutes les 2 minutes
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
