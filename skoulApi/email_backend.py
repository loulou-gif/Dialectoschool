"""
Backend SMTP personnalisé pour résoudre les problèmes de compatibilité
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.mail.backends.smtp import EmailBackend as BaseEmailBackend
from django.core.mail.message import EmailMessage
from django.conf import settings

class CustomEmailBackend(BaseEmailBackend):
    """
    Backend SMTP personnalisé qui gère mieux les connexions Gmail
    """
    
    def open(self):
        """
        Établit une connexion SMTP avec Gmail
        """
        if self.connection:
            return False
            
        try:
            # Créer une connexion SMTP sécurisée
            self.connection = smtplib.SMTP(self.host, self.port)
            
            # Démarrer TLS sans paramètres SSL problématiques
            self.connection.starttls()
            
            # Authentification
            if self.username and self.password:
                self.connection.login(self.username, self.password)
                
            return True
            
        except Exception as e:
            if not self.fail_silently:
                raise
            return False
    
    def send_messages(self, email_messages):
        """
        Envoie les messages email
        """
        if not email_messages:
            return 0
            
        if not self.open():
            return 0
            
        sent = 0
        
        for message in email_messages:
            try:
                sent += self._send_message(message)
            except Exception as e:
                if not self.fail_silently:
                    raise
                print(f"Erreur lors de l'envoi de l'email: {e}")
                
        return sent
    
    def _send_message(self, message):
        """
        Envoie un message email individuel
        """
        try:
            # Créer le message MIME
            msg = MIMEMultipart()
            msg['From'] = message.from_email
            msg['To'] = ', '.join(message.to)
            msg['Subject'] = message.subject
            
            # Ajouter le contenu
            if message.body:
                msg.attach(MIMEText(message.body, 'plain', 'utf-8'))
            
            # Envoyer le message
            self.connection.send_message(msg)
            return 1
            
        except Exception as e:
            print(f"Erreur lors de l'envoi du message: {e}")
            raise
