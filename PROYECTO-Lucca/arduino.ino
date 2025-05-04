#include <SPI.h>             // Librería para comunicación SPI (necesaria para el lector RFID)
#include <MFRC522.h>         // Librería para el módulo lector RFID RC522
#include <Servo.h>           // Librería para controlar servos
#include <DHT.h>             // Librería para sensores DHT (temperatura y humedad)

// --- Definiciones de pines ---

#define SS_PIN 10            // Pin SS del RFID
#define RST_PIN 9            // Pin de reset del RFID

#define DHTPIN 2             // Pin de datos del sensor DHT11
#define DHTTYPE DHT11        // Tipo de sensor (DHT11)

#define RED_LED 5            // Pin del LED rojo (acceso denegado)
#define GREEN_LED 6          // Pin del LED verde (acceso concedido)

#define SERVO_PIN 3          // Pin del servo (cerradura) - De esto tengo que comentar que al final no he usado el servo ya que no tenía el como probarlo en la expo de clase. Por si sirve, en mi casa lo estoy empezando a implementar en un armario de la comunidad que tengo en mi piso. 

// --- Inicialización de objetos ---

MFRC522 rfid(SS_PIN, RST_PIN);  // Objeto para controlar el lector RFID
DHT dht(DHTPIN, DHTTYPE);       // Objeto para leer el sensor DHT
Servo lockServo;                // Objeto para controlar el servo

// --- Variables de estado de la cerradura --- (está en caso de que lo hubiese hecho y para dejarlo implementado ya para mi casa)

int lockPos = 15;           // Ángulo del servo para posición cerrada
int unlockPos = 75;         // Ángulo del servo para posición abierta
boolean locked = true;      // Estado actual de la cerradura (true = cerrada)

// --- Usuarios autorizados y nombres asociados ---

String accessGranted[] = {"3025517163", "19612012715"};  // UID de tarjetas permitidas, se pueden añadir las que sean necesarias
String nomsUsuaris[] = {"Lucca", "Arnau"};               // Nombres correspondientes
int accessGrantedSize = 2;                               // Número de usuarios

// --- Temporizador para lectura de temperatura ---

unsigned long lastTempRead = 0;              // Último tiempo de lectura de temperatura
const unsigned long tempInterval = 10000;    // Intervalo de lectura (10 segundos para que esté actualizado)

// --- Función setup: configuración inicial ---

void setup() {
  Serial.begin(9600);           // Inicia comunicación serie
  SPI.begin();                  // Inicia bus SPI
  rfid.PCD_Init();              // Inicia el lector RFID
  dht.begin();                  // Inicia el sensor DHT

  pinMode(RED_LED, OUTPUT);     // LED rojo como salida
  pinMode(GREEN_LED, OUTPUT);   // LED verde como salida

  lockServo.attach(SERVO_PIN);  // Conecta el servo al pin especificado
  lockServo.write(lockPos);     // Posiciona el servo en cerrado

  Serial.println("Sistema inicialitzat: RFID + Temperatura");  // Mensaje de inicio
}

// --- Función loop: se repite constantemente ---

void loop() {
  // --- Parte 1: Lectura RFID ---
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String temp = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      temp += String(rfid.uid.uidByte[i]);  // Construye el UID como string
    }
    checkAccess(temp);  // Verifica si el UID está autorizado
    rfid.PICC_HaltA();  // Detiene la comunicación con la tarjeta
  }

  // --- Parte 2: Lectura de temperatura/humedad ---
  unsigned long now = millis();
  if (now - lastTempRead > tempInterval) {
    lastTempRead = now;
    float h = dht.readHumidity();        // Lee humedad
    float t = dht.readTemperature();     // Lee temperatura
    if (!isnan(h) && !isnan(t)) {        // Verifica si son valores válidos
      Serial.print("TºC: ");
      Serial.print(t);
      Serial.print("º  Humitat: ");
      Serial.print(h);
      Serial.println("%");
    }
  }
}

// --- Verifica si el UID recibido tiene acceso ---

void checkAccess(String temp) {
  boolean granted = false;

  for (int i = 0; i < accessGrantedSize; i++) {
    if (accessGranted[i] == temp) {  // Si el UID coincide con uno autorizado (los cuales he definido anteriormente)
      granted = true;

      // Imprime registro por consola en formato especial
      Serial.print("USER_LOG:");
      Serial.print(nomsUsuaris[i]);
      Serial.print(",");
      Serial.print(temp);
      Serial.println(",OK");

      toggleLock();             // Cambia estado de la cerradura
      blinkLED(GREEN_LED);      // Parpadea LED verde
    }
  }

  if (!granted) {
    Serial.print("USER_LOG:Desconegut,");  // UID no autorizado
    Serial.print(temp);
    Serial.println(",KO");

    blinkLED(RED_LED);           // Parpadea LED rojo
  }
}

// --- Cambia entre abrir y cerrar la cerradura (lo mismo de antes, de momento no lo he implementado, lo dejo para cuando lo haga en mi casa) ---

void toggleLock() {
  if (locked) {
    lockServo.write(unlockPos);  // Abre
    locked = false;
  } else {
    lockServo.write(lockPos);    // Cierra
    locked = true;
  }
}

// --- Parpadea un LED 3 veces (verde o rojo) ---

void blinkLED(int ledPin) {
  for (int i = 0; i < 3; i++) {
    digitalWrite(ledPin, HIGH);  // Enciende
    delay(200);
    digitalWrite(ledPin, LOW);   // Apaga
    delay(200);
  }
}
