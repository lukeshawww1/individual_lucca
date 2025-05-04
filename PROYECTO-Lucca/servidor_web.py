from flask import Flask, jsonify, request  # Importa Flask y funciones para respuestas JSON y solicitudes HTTP
from flask_cors import CORS  # Para permitir peticiones entre dominios (CORS)
import sqlite3  # Para interactuar con la base de datos SQLite
import paho.mqtt.publish as publish  # Para publicar mensajes MQTT

app = Flask(__name__)  # Crea la aplicación Flask
CORS(app)  # Permite llamadas cruzadas desde otros puertos

# Configuración
DB_PATH = "/home/Lucca/projecte/accesscontrol/access_logs.db"  # Ruta de la bbdd
MQTT_BROKER = "localhost"  # Dirección del broker MQTT
MQTT_PORT = 1883  # Puerto del broker MQTT
TOPIC_LUZ = "casa/luz"  # Tópico para control de luz

# Ruta para obtener la última lectura de temperatura y humedad
@app.route('/ultima_temp')
def ultima_temp():
    conn = sqlite3.connect(DB_PATH)  # Conecta con la bbdd
    cursor = conn.cursor()
    cursor.execute("SELECT temperatura, humitat FROM temps ORDER BY timestamp DESC LIMIT 1")  # Consulta la última entrada
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"temperatura": row[0], "humedad": row[1]})  # Devuelve los datos si existen
    else:
        return jsonify({"temperatura": "N/D", "humedad": "N/D"})  # Si no hay datos

# Ruta para obtener los últimos accesos registrados
@app.route('/ultimos_accesos')
def ultimos_accesos():
    conn = sqlite3.connect(DB_PATH)  # Conecta con la bbdd
    cursor = conn.cursor()
    cursor.execute("SELECT nom, uid, estat, timestamp FROM logs ORDER BY timestamp DESC LIMIT 5")  # Últimos 5 accesos
    rows = cursor.fetchall()
    conn.close()
    # Formatea cada fila como un diccionario
    accesos = [{"nombre": r[0], "uid": r[1], "estado": r[2], "timestamp": r[3]} for r in rows]
    return jsonify(accesos)

# Ruta para encender la luz de una habitación
@app.route('/encender/<habitacion>', methods=['POST'])
def encender(habitacion):
    try:
        publish.single(TOPIC_LUZ, "ON", hostname=MQTT_BROKER, port=MQTT_PORT)  # Publica mensaje ON al tópico
        return jsonify({"resultado": "Luz encendida"})
    except Exception as e:
        return jsonify({"error": str(e)})  # Devuelve error si ocurre

# Ruta para apagar la luz de una habitación
@app.route('/apagar/<habitacion>', methods=['POST'])
def apagar(habitacion):
    try:
        publish.single(TOPIC_LUZ, "OFF", hostname=MQTT_BROKER, port=MQTT_PORT)  # Publica mensaje OFF al tópico
        return jsonify({"resultado": "Luz apagada"})
    except Exception as e:
        return jsonify({"error": str(e)})  # Devuelve error si ocurre

# Inicia la aplicación Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Escucha en todas las interfaces, puerto 5000 para que no coincida con apache
