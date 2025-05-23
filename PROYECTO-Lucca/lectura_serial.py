import serial  # Para comunicación con el puerto serie (Arduino)
import sqlite3  # Para interactuar con la base de datos SQLite
from datetime import datetime  # Para obtener la fecha y hora actual
import re  # Para trabajar con expresiones regulares
import pytz  # Para trabajar con zonas horarias

# Establece la zona horaria a 'Europe/Madrid', esto finalmente no lo uso ya que tengo que introducir la hora de la raspberry manualmente porque se queda el día y la hora del último acceso
zona_horaria = pytz.timezone('Europe/Madrid')

# Conecta con la base de datos SQLite3
conn = sqlite3.connect('/home/Lucca/projecte/accesscontrol/access_logs.db')
cursor = conn.cursor()

# Configura la conexión serie con el Arduino, eL puerto puede ir cambiando ya que cada vez que desconecto y conecto la arduino, tengo que hacer un l /dev/tty* para saber el puerto exacto.
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1) 

print("[INFO] Llegint dades de l'Arduino...")  # Mensaje de inicio

while True:
    try:
        # Lee una línea del puerto serie y la decodifica
        linea = ser.readline().decode('utf-8').strip()

        if not linea:
            continue  # Si la línea está vacía, salta a la siguiente iteración

        print(f"[SERIAL] {linea}")  # Muestra la línea leída del puerto serie

        # Procesa los datos de registro de usuario
        if linea.startswith("USER_LOG:"):
            parts = linea.replace("USER_LOG:", "").split(",")  # Divide los datos

            if len(parts) == 3:
                nombre, uid, estado = parts
                timestamp = datetime.now(zona_horaria).strftime("%Y-%m-%d %H:%M:%S")
                # Inserta los datos en la tabla 'logs'
                cursor.execute(
                    "INSERT INTO logs (nom, uid, estat, timestamp) VALUES (?, ?, ?, ?)",
                    (nombre.strip(), uid.strip(), estado.strip(), timestamp)
                )
                conn.commit()  # Guarda los cambios en la base de datos
                print(f"[ACCESS] {timestamp} - {nombre} ({uid}) - {estado}")

        # procesa los datos de temperatura y humedad
        elif linea.startswith("T°C:"):
            match = re.search(r"T°C:\s*(\d+(?:\.\d+)?)\s+Humitat:\s*(\d+(?:\.\d+)?)%", linea)
            if match:
                temperatura = float(match.group(1))
                humedad = float(match.group(2))
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # inserta los datos en la tabla 'temps' de la bbdd acces.logs.db
                cursor.execute(
                    "INSERT INTO temps (temperatura, humitat, timestamp) VALUES (?, ?, ?)",
                    (temperatura, humedad, timestamp)
                )
                conn.commit()  # Guarda los cambios en la base de datos
                print(f"[TEMP] {timestamp} - {temperatura}°C / {humedad}%") #Información que se imprime

    except Exception as e:
        # captura y muestra cualquier error ocurrido
        print(f"[ERROR] {e}")
