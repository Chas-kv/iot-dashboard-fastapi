#!/bin/bash

echo "Iniciando aplicación en modo producción..."
docker compose -f docker-compose.prod.yml up --build -d

# Esperar unos segundos para que arranque el backend
sleep 5

# Abrir navegador automáticamente (solo si hay entorno gráfico)
xdg-open http://localhost:8000 || echo "Por favor abra su navegador y vaya a http://localhost:8000"
echo "Aplicación en modo producción iniciada."
echo "Para detener la aplicación, use 'docker compose down'."
echo "Para ver los logs, use 'docker compose logs -f'."
echo "Para acceder al contenedor, use 'docker exec -it <nombre_contenedor> /bin/bash'."
echo "¡Listo para usar!"
echo "Recuerda que puedes cambiar a modo desarrollo con 'bash dev.sh'."
echo "Para iniciar el entorno de desarrollo, usa 'bash dev.sh'."
echo "Para iniciar el entorno de producción, usa 'bash prod.sh'."
echo "Para iniciar el entorno de producción, usa 'bash start.sh'."    