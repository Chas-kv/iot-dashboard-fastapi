Write-Host "Iniciando aplicación en modo producción..."
docker compose -f docker-compose.prod.yml up --build -d

Start-Sleep -Seconds 5

Start-Process "http://localhost:8000"
Write-Host "Aplicación en modo producción iniciada."
Write-Host "Para detener la aplicación, use 'docker compose down'."