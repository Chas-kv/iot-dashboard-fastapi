@echo off
echo 🚀 Iniciando la aplicación en modo producción...

:: Validar si Docker está instalado
where docker >nul 2>nul
IF ERRORLEVEL 1 (
    echo ❌ Docker no está instalado. Por favor instálalo primero.
    exit /b 1
)

:: Ejecutar docker-compose en modo producción (modo detach)
docker compose -f docker-compose.prod.yml up --build -d

echo ✅ Aplicación desplegada en segundo plano.
