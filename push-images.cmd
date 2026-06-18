@echo off
REM Simple batch script to push Docker images to DockerHub

echo ==========================================
echo Docker Image Push Script
echo ==========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    exit /b 1
)

echo [INFO] Checking DockerHub login...
docker login
if errorlevel 1 (
    echo [ERROR] Docker login failed
    exit /b 1
)

echo.
echo ==========================================
echo Pushing Frontend Image (Small - Fast)
echo ==========================================
docker push hammadasher/mlops-saylani-frontend:latest
if errorlevel 1 (
    echo [ERROR] Frontend push failed
    set FRONTEND_FAILED=1
) else (
    echo [SUCCESS] Frontend image pushed successfully
)

echo.
echo ==========================================
echo Pushing API Image (Large - May take time)
echo ==========================================
echo This may take 10-30 minutes depending on your internet speed...
echo.
docker push hammadasher/mlops-saylani-api:latest
if errorlevel 1 (
    echo [ERROR] API push failed
    set API_FAILED=1
) else (
    echo [SUCCESS] API image pushed successfully
)

echo.
echo ==========================================
echo Summary
echo ==========================================

if defined FRONTEND_FAILED (
    echo [X] Frontend: FAILED
) else (
    echo [OK] Frontend: SUCCESS
)

if defined API_FAILED (
    echo [X] API: FAILED
    echo.
    echo ALTERNATIVE SOLUTION:
    echo Build the API image directly on EC2 to avoid uploading 2.69GB
    echo See AWS_DEPLOYMENT.md for instructions
) else (
    echo [OK] API: SUCCESS
    echo.
    echo Both images are now on DockerHub!
    echo - https://hub.docker.com/r/hammadasher/mlops-saylani-api
    echo - https://hub.docker.com/r/hammadasher/mlops-saylani-frontend
)

echo ==========================================
pause
