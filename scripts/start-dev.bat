@echo off
echo 🚀 Iniciando la aplicación en modo desarrollo...

:: Validar si Docker está instalado
where docker >nul 2>nul
IF ERRORLEVEL 1 (
    echo ❌ Docker no está instalado. Por favor instálalo primero.
    exit /b 1
)

:: Ejecutar docker-compose en modo desarrollo
docker compose -f docker-compose.dev.yml up --build
echo 🔧 Aplicación en modo desarrollo iniciada.