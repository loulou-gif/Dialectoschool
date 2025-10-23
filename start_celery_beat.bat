@echo off
REM Script pour démarrer Celery Beat (Windows)
REM Ce script lance Celery Beat qui gère automatiquement les devoirs planifiés

echo ========================================
echo   Démarrage de Celery Beat
echo ========================================
echo.
echo Celery Beat va gérer automatiquement :
echo   - Envoi des devoirs planifiés (toutes les 60 secondes)
echo   - Notifications de fin de devoirs (toutes les 120 secondes)
echo.
echo Assurez-vous que Redis est démarré !
echo.
echo Pour arrêter : Appuyez sur CTRL+C
echo ========================================
echo.

cd %~dp0

REM Activer l'environnement virtuel si nécessaire
if exist "..\dialektos_env\Scripts\activate.bat" (
    echo Activation de l'environnement virtuel...
    call ..\dialektos_env\Scripts\activate.bat
)

REM Démarrer Celery Beat
echo Démarrage de Celery Beat...
celery -A dialectoskoul beat --loglevel=info

pause

