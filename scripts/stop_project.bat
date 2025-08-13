@echo off
echo ==========================
echo  Deteniendo Proyecto IoT
echo ==========================

REM 1) Detener Mosquitto (si sigue en ejecución)
echo Cerrando Mosquitto...
taskkill /IM mosquitto.exe /F

REM 2) Detener Uvicorn/FastAPI
echo Cerrando FastAPI (uvicorn)...
for /f "tokens=2" %%a in ('tasklist ^| find "uvicorn.exe"') do taskkill /PID %%a /F

REM 3) O cualquier otro proceso adicional...

echo ==========================
echo  Proyecto IoT detenido.
echo ==========================
pause
