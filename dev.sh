#!/bin/bash
echo "🔧 Iniciando entorno de desarrollo IoT..."
docker-compose -f docker-compose.dev.yml --env-file .env up --build
echo "🚀 Entorno de desarrollo IoT listo."