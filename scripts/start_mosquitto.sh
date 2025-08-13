#!/bin/bash
echo "Iniciando Mosquitto Broker..."
mosquitto -g /etc/mosquitto/mosquitto.conf &
echo "Mosquitto Broker iniciado."
