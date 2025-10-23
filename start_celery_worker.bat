@echo off
REM Script pour démarrer Celery Worker (Windows)
REM Ce script lance le worker Celery qui exécute les tâches en arrière-plan

echo ========================================
echo   Démarrage de Celery Worker
echo ========================================
echo.
echo Le Celery Worker va exécuter les tâches :
echo   - Envoi d'emails
echo   - Traitement asynchrone
echo   - Tâches planifiées
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

REM Démarrer Celery Worker (avec pool=solo pour Windows)
echo Démarrage de Celery Worker...
celery -A dialectoskoul worker --loglevel=info --pool=solo

pause

