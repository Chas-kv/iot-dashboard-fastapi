# 🚀 Proyecto IoT API RESTful con MQTT y Dashboard

Este proyecto implementa un sistema IoT que conecta un **ESP8266** con sensores (DHT11, LDR) y un servomotor, integrando un **broker MQTT**, una **API RESTful** con FastAPI y un **dashboard web** para el control y visualización en tiempo real.

---

## 📌 Características
- **API RESTful** con FastAPI para interactuar con los datos y enviar comandos.
- **Integración MQTT** para comunicación en tiempo real con el ESP8266.
- **Dashboard web** para control y monitoreo de:
  - Estado de la compuerta
  - Modo automático/manual
  - Ángulo del servo
  - Datos de temperatura, humedad y luz
- **Historial de eventos** guardado en archivo JSON.
- **Autenticación** con sesión y JWT.
- **Soporte Docker** para despliegue rápido.
- **Simulador** para pruebas sin hardware físico.

---



## 📂 Estructura del Proyecto

```plaintext
PROYECTO-IoT-API-RESTFUL/
│
├── app/                     # Código fuente principal de la API
│   ├── main.py              # Servidor FastAPI + rutas y lógica principal
│   ├── mqtt_handler.py      # Cliente MQTT y gestión de mensajes
│   ├── models.py            # Modelos Pydantic para validación de datos
│   └── ...                  # Otros módulos de soporte
│
├── static/                  # Archivos CSS y recursos estáticos
├── templates/               # Plantillas HTML (Dashboard)
├── scripts/                 # Scripts para iniciar/detener el proyecto y broker
│
├── datos.json               # Datos actuales (generado en tiempo de ejecución)
├── historial.json           # Historial de eventos (generado en tiempo de ejecución)
│
├── requirements.txt         # Dependencias de Python
├── Dockerfile               # Configuración para construcción en Docker
├── docker-compose.*.yml     # Configuración para orquestación con Docker Compose
│
├── README.md                # Documentación principal del proyecto
└── .gitignore               # Archivos y carpetas ignorados por Git



---

## ⚙️ Instalación y ejecución

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/usuario/proyecto-iot-api.git
cd proyecto-iot-api
```
## Crear entorno virtual

python -m venv IoT_env
source IoT_env/bin/activate  # Linux / Mac
IoT_env\Scripts\activate     # Windows
## Instalar dependencias
pip install -r requirements.txt

## Configurar variables de entorno
Crear un archivo .env en laraiz  del proyecto con contenido similar:
SESSION_SECRET=clave_sesion_segura
JWT_SECRET=clave_jwt_segura
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USER=usuario_mqtt
MQTT_PASSWORD=contraseña_mqtt
IOT_USERNAME=usuario_panel
IOT_PASSWORD=contraseña_panel
## Iiniciar el servidor
```bash
python -m app.main
```
**El dashboard estara disponible en:**

http://127.0.0.1:8000/panel

## Simulacion sin hardware
Puedes usar el archivo simulador.py para enviar datos MQTT falsos y probar la interfaz:

```bash
python simulador.py
```
## Uso con Docker

```bash
docker-compose -f docker-compose.dev.yml up --build
```
## 🔐 Autenticación y seguridad

- El panel requiere login con usuario y contraseña.

- La API expone rutas protegidas con JWT.

- MQTT requiere credenciales (si el broker está configurado para ello).

📜 Licencia

Este proyecto es de uso personal y educativo. No se autoriza su uso comercial sin permiso previo.

## 💡 Desarrollado como parte de un proyecto de IoT integrando hardware, backend y frontend.
