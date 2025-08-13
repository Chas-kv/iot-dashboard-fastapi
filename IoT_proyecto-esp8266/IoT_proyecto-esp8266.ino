#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Servo.h>

#define DHTPIN D2
#define DHTTYPE DHT11
#define LDRPIN A0
#define SERVOPIN D0

DHT dht(DHTPIN, DHTTYPE);
Servo servoMotor;

// WiFi
const char* ssid = "FLIA OLARTE";
const char* password = "minutoainterneta1000";

// MQTT (local)
const char* mqtt_server = "192.168.1.47";  // IP de tu PC donde corre Mosquitto
WiFiClient espClient;
PubSubClient client(espClient);

// MQTT topics
#define TOPIC_TEMP       "iot/esp8266/temperature"
#define TOPIC_HUM        "iot/esp8266/humidity"
#define TOPIC_LUMEN      "iot/esp8266/lumen"
#define TOPIC_SERVO      "iot/esp8266/servo_value"
#define TOPIC_STATE      "iot/esp8266/door_state"
#define TOPIC_MODE_CMD   "mode"
#define TOPIC_SERVO_CMD  "servo"

// Estado del sistema
int modo = 1;              // 1: automático, 0: manual
int angulo_manual = 90;    // ángulo de servo en modo manual
unsigned long lastMsg = 0;
const long intervalo = 5000;

int intentos_mqtt = 0;

void setup_wifi() {
  Serial.print("Conectando a WiFi ");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" conectado.");
}

void callback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (int i = 0; i < length; i++) msg += (char)payload[i];

  Serial.printf("📥 Topic: %s → %s\n", topic, msg.c_str());

  if (String(topic) == TOPIC_MODE_CMD) {
    modo = msg.toInt();
    Serial.printf("🔁 Modo cambiado a: %s\n", modo == 1 ? "Automático" : "Manual");
  }

  if (String(topic) == TOPIC_SERVO_CMD && modo == 0) {
    angulo_manual = constrain(msg.toInt(), 0, 180);
    servoMotor.write(angulo_manual);
    Serial.printf("🔧 Servo manual a: %d°\n", angulo_manual);
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    if (client.connect("ESP8266Client")) {
      Serial.println("✅ Conectado");
      client.subscribe(TOPIC_MODE_CMD);
      client.subscribe(TOPIC_SERVO_CMD);
      intentos_mqtt = 0;
    } else {
      Serial.printf("❌ Falla (%d). Esperando 5 seg\n", client.state());
      delay(5000);
      intentos_mqtt++;
      if (intentos_mqtt >= 10) {
        Serial.println("🔁 Reiniciando ESP por fallos MQTT...");
        ESP.restart();
      }
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  servoMotor.attach(SERVOPIN);
  servoMotor.write(90); // posición inicial

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi perdido, reconectando...");
    setup_wifi();
  }

  if (!client.connected()) reconnect();
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > intervalo) {
    lastMsg = now;

    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    int ldr = analogRead(LDRPIN);

    if (!isnan(temp)) client.publish(TOPIC_TEMP, String(temp).c_str());
    if (!isnan(hum))  client.publish(TOPIC_HUM, String(hum).c_str());

    client.publish(TOPIC_LUMEN, String(ldr).c_str());

    if (modo == 1) {
      if (ldr > 600) {
        servoMotor.write(0);
        client.publish(TOPIC_STATE, "true"); // puerta abierta
      } else {
        servoMotor.write(90);
        client.publish(TOPIC_STATE, "false"); // puerta cerrada
      }
    } else {
      servoMotor.write(angulo_manual);
      bool abierta = angulo_manual < 90;
      client.publish(TOPIC_STATE, abierta ? "true" : "false");
    }

    int posicion = servoMotor.read();
    client.publish(TOPIC_SERVO, String(posicion).c_str());

    Serial.printf("📤 T: %.1f°C | H: %.1f%% | Luz: %d | Servo: %d° | Estado: %s\n",
                  temp, hum, ldr, posicion,
                  (posicion < 90 ? "Abierta" : "Cerrada"));
  }
}
