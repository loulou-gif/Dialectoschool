import time
from django.utils.deprecation import MiddlewareMixin
from .models import APILogEntry
from django.conf import settings
import re
import json

# Liste des champs sensibles à masquer
SENSITIVE_FIELDS = ['password', 'pass', 'pwd']

def clean_multipart_body(raw_body):
    # 1️⃣ Supprimer tous les WebKit boundaries
    cleaned = re.sub(r'-+WebKitFormBoundary.*?\r\n', '', raw_body, flags=re.DOTALL)

    # 2️⃣ Séparer par lignes
    lines = cleaned.split('\r\n')
    data = {}
    key = None

    for line in lines:
        if line.startswith('Content-Disposition: form-data;'):
            # Chercher le nom du champ
            match = re.search(r'name="([^"]+)"', line)
            if match:
                key = match.group(1)
        elif key and line.strip() != '':
            value = line.strip()

            # 3️⃣ Vérifie si le champ est sensible
            if key.lower() in SENSITIVE_FIELDS:
                value = "*****"  # Masquer la vraie valeur

            data[key] = value
            key = None

    return json.dumps(data, indent=2)



class APILoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # On note l'heure à laquelle la requête commence
        request.start_time = time.time()
        
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                request._body_copy = request.body.decode('utf-8')
            except Exception:
                request._body_copy = ''

    def process_response(self, request, response):
        # Seulement si l'URL commence par /api/
        if request.path.startswith('/api/') and request.method != "GET":
            duration = time.time() - getattr(request, 'start_time', time.time())

            # Récupère l'IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            # Récupère l'utilisateur
            user = request.user if request.user.is_authenticated else None

            # Récupère le body de la requête (mais attention seulement sur POST/PUT/PATCH)
            body_raw  = getattr(request, '_body_copy', '')
            body_clean =''
            if body_raw:
                body_clean = clean_multipart_body(body_raw)
                
            # Enregistre dans la base
            APILogEntry.objects.create(
                user=user,
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                ip_address=ip,
                request_body=body_clean  ,
                duration=duration
            )

        return response
