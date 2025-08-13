#!/bin/bash

echo "🚀 Iniciando la aplicación en modo producción..."

# Validar si Docker está instalado
if ! command -v docker &> /dev/null
then
    echo "❌ Docker no está instalado. Por favor instálalo primero."
    exit 1
fi

# Usar docker-compose.prod.yml para levantar la app
docker compose -f docker-compose.prod.yml up --build -d

echo "✅ Aplicación desplegada en segundo plano."
