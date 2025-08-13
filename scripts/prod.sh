#!/bin/bash
echo "🚀 Iniciando entorno de producción IoT..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
echo "🌟 Entorno de producción IoT listo."