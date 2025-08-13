#!/bin/bash

echo "🚀 Iniciando la aplicación en modo desarrollo..."

# Validar si Docker está instalado
if ! command -v docker &> /dev/null
then
    echo "❌ Docker no está instalado. Por favor instálalo primero."
    exit 1
fi

# Usar docker-compose.dev.yml para levantar la app
docker compose -f docker-compose.dev.yml up --build
echo "🔧 Aplicación en modo desarrollo iniciada."