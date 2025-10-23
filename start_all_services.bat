@echo off
echo ========================================
echo Demarrage de tous les services
echo ========================================
echo.

REM Vérifier si nous sommes dans le bon répertoire
if not exist "manage.py" (
    echo ERREUR: manage.py non trouve
    echo Assurez-vous d'etre dans le repertoire dialectoskoul
    pause
    exit /b 1
)

echo [1/4] Demarrage de Redis...
start "Redis Server" cmd /k "redis-server || echo ERREUR: Redis non installe. Telechargez depuis https://github.com/microsoftarchive/redis/releases"

timeout /t 3 /nobreak > nul

echo [2/4] Demarrage de Celery Worker...
start "Celery Worker" cmd /k "celery -A dialectoskoul worker --loglevel=info --pool=solo"

timeout /t 3 /nobreak > nul

echo [3/4] Demarrage de Celery Beat...
start "Celery Beat" cmd /k "celery -A dialectoskoul beat --loglevel=info"

timeout /t 3 /nobreak > nul

echo [4/4] Demarrage de Django...
start "Django Server" cmd /k "python manage.py runserver"

echo.
echo ========================================
echo Tous les services sont demarres!
echo ========================================
echo.
echo 4 fenetres de terminal ont ete ouvertes:
echo   1. Redis Server
echo   2. Celery Worker
echo   3. Celery Beat
echo   4. Django Server
echo.
echo Pour arreter tous les services:
echo   - Fermez toutes les fenetres de terminal
echo   - Ou appuyez sur Ctrl+C dans chaque fenetre
echo.
echo Le systeme d'envoi automatique est maintenant actif!
echo.
pause

