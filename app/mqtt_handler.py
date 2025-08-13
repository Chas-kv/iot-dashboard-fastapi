# mqtt_handler.py
import os
import time
import logging
import threading
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
# app/mqtt_handler.py
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPICS = [("test/topic", 0)]  # Lista de tópicos y QoS

client = mqtt.Client()

# Variable para almacenar el callback registrado
_message_callback = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado al broker MQTT")
        for topic, qos in TOPICS:
            client.subscribe(topic, qos)
    else:
        print(f"❌ Error de conexión: {rc}")

def on_message(client, userdata, msg):
    mensaje = msg.payload.decode()
    print(f"📩 Mensaje recibido en {msg.topic}: {mensaje}")
    if _message_callback:
        _message_callback(msg.topic, mensaje)

def register_message_callback(callback):
    """
    Registra una función callback para manejar mensajes MQTT.
    La función debe aceptar 2 parámetros: topic y mensaje.
    """
    global _message_callback
    _message_callback = callback

def publish(topic, message):
    client.publish(topic, message)

def start_mqtt():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()

load_dotenv()  # para leer MQTT_* desde .env si existen

logger = logging.getLogger("mqtt_handler")
logging.basicConfig(level=logging.INFO)

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "iot_dashboard_client")

# definir topics como dict para publicar por key
TOPICS = {
    "temperature": "iot/esp8266/temperature",
    "humidity": "iot/esp8266/humidity",
    "lumen": "iot/esp8266/lumen",
    "servo_value": "iot/esp8266/servo_value",
    "door_state": "iot/esp8266/door_state",
    "mode": "iot/esp8266/mode"  # opcional
}

# callback registrable para avisar al main cuando llega un mensaje
_message_callback = None

def register_message_callback(func):
    """Registra una función: func(topic: str, payload: str)"""
    global _message_callback
    _message_callback = func

# cliente mqtt global
_client = None

def on_connect(client, userdata, flags, rc):
    logger.info("Conectado a MQTT con rc=%s", rc)
    # suscribirse a todos los topics importantes
    for t in TOPICS.values():
        client.subscribe(t)
        logger.info("Suscrito a %s", t)

def on_message(client, userdata, msg):
    payload = None
    try:
        payload = msg.payload.decode("utf-8")
    except Exception as e:
        logger.warning("No se pudo decodificar payload: %s", e)
        return

    # protección ligera: ignorar payloads muy grandes
    if payload is None or len(payload) > 3000:
        logger.warning("Payload demasiado grande o vacío; descartado.")
        return

    # llamar callback registrado (si existe)
    if _message_callback:
        try:
            _message_callback(msg.topic, payload)
        except Exception as e:
            logger.exception("Error en message_callback: %s", e)
    else:
        logger.info("Mensaje recibido pero no hay callback registrado: %s -> %s", msg.topic, payload)

def _build_client():
    global _client
    _client = mqtt.Client(client_id=MQTT_CLIENT_ID, clean_session=True)
    if MQTT_USER and MQTT_PASSWORD:
        _client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    _client.on_connect = on_connect
    _client.on_message = on_message
    return _client

def start_mqtt():
    """Conecta al broker y mantiene el loop en background (blocking)."""
    client = _build_client()
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    except Exception as e:
        logger.exception("Error conectando al broker MQTT: %s", e)
        # reintento simple (no bloquear forever si falla)
        time.sleep(2)
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        except Exception as e2:
            logger.exception("Segundo intento falló: %s", e2)
            raise

    # usar loop_start para correr en background thread
    client.loop_start()

def publish(topic_key: str, value):
    """Publica un valor al topic correspondiente."""
    if topic_key not in TOPICS:
        raise ValueError("Topic key no definido: " + topic_key)
    if _client is None:
        # intentar reconstruir cliente si no creado
        _build_client()
    # publish y log
    topic = TOPICS[topic_key]
    payload = str(value)
    logger.info("Publicando %s -> %s", topic, payload)
    _client.publish(topic, payload)
