import cv2  # Librería para trabajar con video y visión por computadora
import datetime  # Para obtener fecha y hora actual
import time  # Para pausas y control de tiempo
import smtplib  # Para enviar correos electrónicos
import os  # Para trabajar con el sistema de archivos
from email.mime.multipart import MIMEMultipart  # Para construir correos con adjuntos
from email.mime.base import MIMEBase
from email import encoders  # Para codificar adjuntos en base64

# --- Configuración ---

RTSP_URL = "rtsp://CAMPRUEBA:Chiellini2015@192.168.1.22:554/stream1"  # Dirección RTSP de la cámara con user y password paraacceder a través de VLC
VIDEO_OUTPUT_DIR = "./videos"  # Carpeta donde se guardarán los videos grabados (es dentro de projecte/camara/videos)
FPS = 20  # Para que vaya medianamente fluido
DURACION_VIDEO_SEGUNDOS = 15  # Duración del video grabado
FRAMES_A_GRABAR = FPS * DURACION_VIDEO_SEGUNDOS  # Número total de frames a grabar

# Configuración smtp
EMAIL_USUARIO = "luccacastellarnau05@gmail.com"
EMAIL_CONTRASENA = "mnfw whlb qfan unyb"
EMAIL_DESTINO = "luccacastellarnau05@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Rango horario en el que se considera "no autorizado"
HORA_INICIO = 22  # Desde las 22:00
HORA_FIN = 6     # Hasta las 6:00

# Crea la carpeta de salida si no existe (la carpeta projecte/camara/videos)
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)

# Verifica si la hora actual está fuera del horario permitido
def es_horario_no_autorizado():
    hora = datetime.datetime.now().hour
    return hora >= HORA_INICIO or hora < HORA_FIN

# Envía un correo con el video como adjunto
def enviar_correo(ruta_video):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USUARIO
        msg["To"] = EMAIL_DESTINO
        msg["Subject"] = "ALERTA: Movimiento detectado"

        # Adjunta el archivo de video
        adjunto = MIMEBase("application", "octet-stream")
        with open(ruta_video, "rb") as f:
            adjunto.set_payload(f.read())
        encoders.encode_base64(adjunto)
        adjunto.add_header("Content-Disposition", f"attachment; filename=" + os.path.basename(ruta_video))
        msg.attach(adjunto)

        # Envío del correo
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USUARIO, EMAIL_CONTRASENA)
        server.sendmail(EMAIL_USUARIO, EMAIL_DESTINO, msg.as_string())
        server.quit()
        print(f"[INFO] Correo enviado con video: {os.path.basename(ruta_video)}")
    except Exception as e:
        print(f"[ERROR] Falló el envío del correo: {e}")

# Graba un video desde la cámara con al duración que he definido antes. En esto he usado IA ya que me estaba costando mucho captar el movimiento sin usar la propia app de Tapo o sin usar un sensor pir. Al principio probé de enviar una sola imagen pero imposible.
def grabar_video(cap):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Nombre único por fecha/hora
    nombre_video = os.path.join(VIDEO_OUTPUT_DIR, f"mov_{timestamp}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codificador para MP4
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(nombre_video, fourcc, FPS, (width, height))

    frames_grabados = 0
    print(f"[INFO] Grabando vídeo {nombre_video} durante {DURACION_VIDEO_SEGUNDOS} segundos...")
    while frames_grabados < FRAMES_A_GRABAR:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] No se pudo leer frame.")
            break
        out.write(frame)
        frames_grabados += 1
        time.sleep(1 / FPS)  # Mantiene la velocidad de grabación

    out.release()
    return nombre_video

# Función principal de detección y respuesta
def main():
    print("[INFO] Iniciando monitorización...")
    cap = cv2.VideoCapture(RTSP_URL)  # Conexión a la cámara
    if not cap.isOpened():
        print("[ERROR] No se pudo acceder a la cámara.")
        return

    # Lee dos frames iniciales
    _, frame1 = cap.read()
    _, frame2 = cap.read()

    while True:
        # Detección de diferencia entre frames consecutivos. Esto lo hace para que cuando cambie la info que se recibe a través de los frames, será que ha detactado el movimiento.
        # Convierte ambos frames a escala de grises y calcula la diferencia absoluta entre ellos
        diff = cv2.absdiff(cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY), 
                   cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY))  # resalta las zonas donde el contenido cambió (posible movimiento)

        # Aplica desenfoque para reducir ruido y captar detalles pequeños
        blur = cv2.GaussianBlur(diff, (5, 5), 0)  # ayuda a eliminar pequeñas variaciones irrelevantes

        # Aplica un umbral: convierte a blanco (255) las diferencias mayores a 20, y negro (0) el resto
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)  # destaca claramente las zonas con diferencias importantes

        # Diluye las zonas blancas para hacerlas más grandes y facilitar la detección de formas completas
        dilated = cv2.dilate(thresh, None, iterations=2)  # expande las áreas de movimiento

        # Busca contornos en la imagen dilatada (zonas donde se detectó movimiento)
        contornos, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # devuelve una lista de contornos detectados


        # Detecta si hay movimiento con área significativa (aquí se debe de ajustar la sensibilidad según lo que se necesite, a mi esto cuando lo intenté con imágenes me daba muchos problemas y lo tenía que estar disminuyendo y aumentando cad 2x3)
        movimiento = any(cv2.contourArea(c) > 5000 for c in contornos)

        if movimiento and es_horario_no_autorizado():
            print("[ALERTA] Movimiento detectado fuera de horario.")
            video_path = grabar_video(cap)  # Graba video del evento
            enviar_correo(video_path)       # Envía alerta por email
            print("[INFO] Esperando 30s antes de nueva detección...")
            time.sleep(30)  # Espera para evitar múltiples alertas seguidas (esto porque al principio enviaba demasiados mails)

        # Actualiza los frames
        frame1 = frame2
        ret, frame2 = cap.read()
        if not ret:
            print("[ERROR] No se pudo leer nuevo frame.")
            break

    cap.release()  # Libera la cámara al finalizar

# Punto de entrada
if __name__ == "__main__":
    main()
