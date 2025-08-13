@echo off
echo ==========================
echo  Iniciando Proyecto IoT
echo ==========================
REM 1) Activar entorno virtual
call IoT_env\Scripts\activate

REM 2) Iniciar Mosquitto Broker
echo Iniciando Mosquitto Broker...
start /B "" "G:\Aplicaciones\Mosquito\mosquitto.exe" -v
timeout /t 2

REM 3) Iniciar API FastAPI en modo desarrollo (puedes cambiar a prod)
echo Iniciando API FastAPI...
start /B uvicorn main:app --host 0.0.0.0 --port 8000 --reload

REM 4) Iniciar Simulador de Sensores (opcional)
REM start /B python simulador.py

echo ==========================
echo  Proyecto IoT Iniciado
echo ==========================
pause
