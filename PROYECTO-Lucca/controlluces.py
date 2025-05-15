iimport paho.mqtt.client as mqtt  # Importa la librería MQTT para Python

# Función que se ejecuta al conectar con el broker MQTT
def on_connect(client, userdata, flags, rc):
    print("[INFO] Conectado con código:", rc)  # Código de resultado de la conexión
    client.subscribe("casa/luz")  # Se suscribe al tópico 'casa/luz' para publicarlo a la web después
    print("[INFO] Suscrito al topic 'casa/luz'")

# Función que se ejecuta cuando se recibe un mensaje en un tópico suscrito
def on_message(client, userdata, msg):
    comando = msg.payload.decode()  # Decodifica el mensaje recibido para que pueda ser leído e interpretado
    print("[INFO] Mensaje recibido:", comando)

    # Verifica el comando y publica la orden que le doy. El tópico lo he cambiado ya que también se lo he cambiado a la bombilla.
    if comando == "ON":
        print("[INFO] Enviando comando de encendido a bombilla...")
        client.publish("shellies/shellies/color/0/command", "on")
    elif comando == "OFF":
        print("[INFO] Enviando comando de apagado a bombilla...")
        client.publish("shellies/shellies/color/0/command", "off")
    else:
        print("[ERROR] Comando desconocido:", comando)

# Crea una instancia del cliente MQTT
mqtt_client = mqtt.Client()

# Asigna las funciones de callback
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Conecta al broker MQTT en localhost por el puerto 1883 con un keepalive de 60 segundos para mantenerlo activo
mqtt_client.connect("localhost", 1883, 60)

# Mantiene el cliente en ejecución para seguir recibiendo mensajes
mqtt_client.loop_forever()
