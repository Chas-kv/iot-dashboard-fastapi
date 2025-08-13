import paho.mqtt.client as mqtt
import json
import os

# Diccionario para guardar los últimos datos recibidos
device_data = {
    "temperature": None,
    "humidity": None,
    "lumen": None,
    "servo_value": None,
    "door_state": None
}

DATA_FILE = "datos.json"

# Guardar datos en archivo JSON
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(device_data, f)

# Cargar datos si ya existen al iniciar
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        try:
            saved = json.load(f)
            device_data.update(saved)
        except Exception:
            pass

# Callback cuando se establece conexión con el broker
def on_connect(client, userdata, flags, rc):
    print("✅ Conectado al broker MQTT con código:", rc)
    client.subscribe("iot/esp8266/#")  # Suscribirse a todos los tópicos del dispositivo

# Callback cuando se recibe un mensaje del broker
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8")
    print(f"📥 Mensaje recibido → {topic}: {payload}")

    if topic.endswith("temperature"):
        device_data["temperature"] = float(payload)
    elif topic.endswith("humidity"):
        device_data["humidity"] = float(payload)
    elif topic.endswith("lumen"):
        device_data["lumen"] = int(payload)
    elif topic.endswith("servo_value"):
        device_data["servo_value"] = int(payload)
    elif topic.endswith("door_state"):
        device_data["door_state"] = (payload.lower() == "true")

    save_data()

# Configuración del cliente MQTT
mqtt_broker = "localhost"
mqtt_port = 1883
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Conexión al broker
client.connect(mqtt_broker, mqtt_port, keepalive=60)

print("🔄 Esperando mensajes MQTT...")
client.loop_start()  # No bloqueante, ideal para integrarlo con FastAPI

# Si deseas usar este archivo directamente, usa loop_forever en lugar de loop_start
# client.loop_forever()
