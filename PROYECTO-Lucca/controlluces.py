import paho.mqtt.client as mqtt  # Importa la librería MQTT para Python

# Función que se ejecuta al conectar con el broker MQTT
def on_connect(client, userdata, flags, rc):
    print("[INFO] Conectado con código:", rc)  # Código de resultado de la conexión
    client.subscribe("casa/luz")  # Se suscribe al tópico 'casa/luz'
    print("[INFO] Suscrito al topic 'casa/luz'")

# Función que se ejecuta cuando se recibe un mensaje en un tópico suscrito
def on_message(client, userdata, msg):
    comando = msg.payload.decode()  # Decodifica el mensaje recibido
    print("[INFO] Mensaje recibido:", comando)

    # Verifica el comando y publica la orden correspondiente
    if comando == "ON":
        print("[INFO] Enviando comando de encendido a bombilla...")
        client.publish("shellies/shellycolorbulb-FCF5C4B2D978/color/0/command", "on")
    elif comando == "OFF":
        print("[INFO] Enviando comando de apagado a bombilla...")
        client.publish("shellies/shellycolorbulb-FCF5C4B2D978/color/0/command", "off")
    else:
        print("[ERROR] Comando desconocido:", comando)

# Crea una instancia del cliente MQTT
mqtt_client = mqtt.Client()

# Asigna las funciones de callback
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Conecta al broker MQTT en localhost por el puerto 1883 con un keepalive de 60 segundos
mqtt_client.connect("localhost", 1883, 60)

# Mantiene el cliente en ejecución para seguir recibiendo mensajes
mqtt_client.loop_forever()
