import paho.mqtt.client as mqtt
import time
import random

# Configuración MQTT
BROKER = "localhost"
PORT = 1883
TOPICS = {
    "temperature": "iot/esp8266/temperature",
    "humidity": "iot/esp8266/humidity",
    "lumen": "iot/esp8266/lumen",
    "servo_value": "iot/esp8266/servo_value",
    "door_state": "iot/esp8266/door_state",
    "modo": "iot/esp8266/mode",       # Simulación adicional
    "manual_input": "servo_manual"    # Comando en modo manual
}

# Estado del sistema
estado = {
    "modo": 1,  # 1 = automático, 0 = manual
    "angulo": 0,
    "door_state": False
}

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("✅ Conectado a MQTT con código:", rc)
    client.subscribe(TOPICS["manual_input"])  # Escucha comandos del slider

def on_message(client, userdata, msg):
    if msg.topic == TOPICS["manual_input"]:
        try:
            angulo = int(msg.payload.decode())
            estado["angulo"] = angulo
            estado["door_state"] = angulo >= 90
            print(f"🎮 Modo manual: Ángulo recibido {angulo}° → Puerta {'Abierta' if estado['door_state'] else 'Cerrada'}")
        except:
            print("⚠️ Error procesando ángulo manual")

client.on_connect = on_connect
client.on_message = on_message

def publicar_estado():
    # Publicar estado común (servo y puerta)
    client.publish(TOPICS["servo_value"], str(estado["angulo"]))
    client.publish(TOPICS["door_state"], str(estado["door_state"]).lower())

def loop_simulacion():
    tiempo_modo = 0
    while True:
        # Alternar modo cada 60 segundos
        if tiempo_modo % 60 == 0:
            estado["modo"] = 1 - estado["modo"]  # 1 → 0, 0 → 1
            print(f"\n🔁 Modo cambiado a {'Automático' if estado['modo'] else 'Manual'}\n")

        if estado["modo"] == 1:
            # Automático → publica sensores y decide el ángulo
            temp = round(random.uniform(20, 30), 1)
            hum = round(random.uniform(40, 70), 1)
            lumen = random.randint(200, 1000)
            estado["angulo"] = random.choice([0, 90, 180])
            estado["door_state"] = estado["angulo"] >= 90

            client.publish(TOPICS["temperature"], str(temp))
            client.publish(TOPICS["humidity"], str(hum))
            client.publish(TOPICS["lumen"], str(lumen))
            publicar_estado()

            print(f"🌡️ Auto | T: {temp}°C | H: {hum}% | L: {lumen} | A: {estado['angulo']}° | Puerta: {'Abierta' if estado['door_state'] else 'Cerrada'}")

        else:
            # Manual → solo publica servo y puerta según ángulo recibido
            publicar_estado()
            print(f"🔧 Manual | Servo: {estado['angulo']}° → Puerta: {'Abierta' if estado['door_state'] else 'Cerrada'}")

        tiempo_modo += 5
        time.sleep(5)

# ---------- INICIO ----------
if __name__ == "__main__":
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    loop_simulacion()
