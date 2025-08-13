# config.py

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# Si más adelante activas autenticación, cambia esto
MQTT_USER = "Proyecto IoT 1"  # ejemplo: "usuarioiot"
MQTT_PASSWORD = "FastApi1"  # ejemplo: "clave123"

MQTT_CLIENT_ID = "fastapi_iot_backend"

TOPICS = {
    "temperature": "iot/esp8266/temperature",
    "humidity": "iot/esp8266/humidity",
    "lumen": "iot/esp8266/lumen",
    "servo_value": "iot/esp8266/servo_value",
    "door_state": "iot/esp8266/door_state",
    "mode": "iot/esp8266/mode",
    "servo": "iot/esp8266/servo"
}
