import cv2
import numpy as np
import face_recognition
import threading
from datetime import datetime, timedelta
from camaras.sdk_dahua import obtener_total_canales

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton
)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QImage, QPixmap

# Tus importaciones de backend existentes
from database.db import conectar
from recognition.personas import cargar_personas
from recognition.detector import detectar_rostros
from camaras.rtsp_camera import abrir_camara

from services.personas_service import buscar_persona_id
from services.detecciones_service import guardar_deteccion
from logs.logger import escribir_log, escribir_error
from config.config import TIEMPO_REPETICION


class VideoThread(QThread):
    frame_signal = Signal(QImage)

    def __init__(self, camara_id, nombre_camara, rtsp_url):
        super().__init__()
        self.camara_id = camara_id
        self.nombre_camara = nombre_camara
        self.rtsp_url = rtsp_url
        self._run_flag = True
        self.is_running_capture = True

    def run(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            print(f"[INFO] Conectado a PostgreSQL para cámara: {self.nombre_camara}")
        except Exception as e:
            escribir_error(e)
            print("[ERROR] Error PostgreSQL en hilo de video:", e)
            return

        caras_conocidas, nombres = cargar_personas()
        ultimas_detecciones = {}

        # Intentar abrir la cámara con tu función personalizada
        cap = abrir_camara(self.rtsp_url)
        if cap is None:
            mensaje = f"No se pudo abrir la cámara {self.nombre_camara} en {self.rtsp_url}"
            escribir_error(mensaje)
            print(f"[ERROR] {mensaje}")
            return

        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # HILO INTERNO DE CAPTURA (Lógica anti-delay)
        frame_actual = None
        lock = threading.Lock()

        def actualizar_frame():
            nonlocal frame_actual
            while self.is_running_capture:
                ret, frame = cap.read()
                if ret:
                    with lock:
                        frame_actual = frame

        hilo_captura = threading.Thread(target=actualizar_frame, daemon=True)
        hilo_captura.start()

        contador_frames = 0
        ubicaciones = []
        encodings = []

        while self._run_flag:
            with lock:
                if frame_actual is None:
                    continue
                frame = frame_actual.copy()

            contador_frames += 1

            if contador_frames % 10 == 0:
                frame_np = np.array(frame, dtype=np.uint8)
                rgb = cv2.cvtColor(frame_np, cv2.COLOR_BGR2RGB)
                ubicaciones, encodings = detectar_rostros(rgb)

            for (top, right, bottom, left), encoding in zip(ubicaciones, encodings):
                nombre = "Desconocido"
                coincidencias = face_recognition.compare_faces(caras_conocidas, encoding)

                if True in coincidencias:
                    indice = coincidencias.index(True)
                    nombre = nombres[indice]
                    ahora = datetime.now()
                    guardar = False

                    if nombre not in ultimas_detecciones:
                        guardar = True
                    else:
                        diferencia = ahora - ultimas_detecciones[nombre]
                        guardar = diferencia > timedelta(seconds=TIEMPO_REPETICION)

                    if guardar:
                        try:
                            persona_id = buscar_persona_id(cursor, nombre)
                            
                            if persona_id is not None:
                                # Usamos directamente el self.camara_id mapeado desde la UI
                                guardar_deteccion(cursor, conn, persona_id, self.camara_id, ahora)
                                ultimas_detecciones[nombre] = ahora
                                mensaje = f"{nombre} detectado en {self.nombre_camara}"
                                print(f"[OK] {nombre} registrado en {self.nombre_camara}.")
                                escribir_log(mensaje)
                            else:
                                escribir_error(f"No existe la persona en la BD: {nombre}")
                        except Exception as e:
                            conn.rollback()
                            escribir_error(e)
                            print("Error insertando detección:", e)

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, nombre, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.frame_signal.emit(q_image)

        self.is_running_capture = False
        hilo_captura.join(timeout=1)
        cap.release()
        cursor.close()
        conn.close()

    def stop(self):
        self._run_flag = False
        self.is_running_capture = False
        self.wait()


class CameraView(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # --- PANEL DE CONTROL SUPERIOR ---
        control_layout = QHBoxLayout()
        
        self.combo_camaras = QComboBox()
        self.combo_camaras.setStyleSheet("padding: 6px; font-size: 14px; background-color: #1e293b; color: white; border-radius: 4px;")
        self.combo_camaras.currentIndexChanged.connect(self.actualizar_visibilidad_canales)
        
        # Selector de canal dinámico para NVR
        self.lbl_canal = QLabel("Canal:")
        self.lbl_canal.setVisible(False)
        self.combo_canales = QComboBox()
        self.combo_canales.setStyleSheet("padding: 6px; font-size: 14px; background-color: #1e293b; color: white; border-radius: 4px;")
        self.combo_canales.setVisible(False)

        self.btn_conectar = QPushButton("▶️ Conectar")
        self.btn_conectar.setStyleSheet("background-color: #22c55e; color: white; padding: 8px 15px; font-weight: bold; border-radius: 4px;")
        self.btn_conectar.clicked.connect(self.iniciar_video)

        self.btn_desconectar = QPushButton("⏹️ Desconectar")
        self.btn_desconectar.setStyleSheet("background-color: #ef4444; color: white; padding: 8px 15px; font-weight: bold; border-radius: 4px;")
        self.btn_desconectar.clicked.connect(self.detener_video)
        self.btn_desconectar.setEnabled(False)

        control_layout.addWidget(QLabel("Seleccionar origen:"))
        control_layout.addWidget(self.combo_camaras, stretch=1)
        control_layout.addWidget(self.lbl_canal)
        control_layout.addWidget(self.combo_canales)
        control_layout.addWidget(self.btn_conectar)
        control_layout.addWidget(self.btn_desconectar)
        layout.addLayout(control_layout)

        # --- ÁREA DE VIDEO ---
        self.image_label = QLabel("Seleccione una cámara de la lista y presione Conectar")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #0f172a; 
            color: #94a3b8; 
            font-size: 16px; 
            font-weight: bold;
            border-radius: 8px;
        """)
        layout.addWidget(self.image_label, stretch=1)

        # Llenar el combo box al inicializar la vista
        self.actualizar_lista_camaras()

    def actualizar_lista_camaras(self):
        """Consulta la base de datos y guarda los datos crudos en el ComboBox."""
        self.combo_camaras.clear()
        
        # Opción por si quieres hacer pruebas con tu webcam física sin RTSP
        self.combo_camaras.addItem("📸 Cámara Web Integrada (Local)", {"id": 0, "nombre": "Webcam Local", "tipo": "WEB", "url": 0})

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, tipo, ip, puerto, usuario, password, canal FROM camaras")
            camaras = cursor.fetchall()
            
            for c in camaras:
                cid, nombre, tipo, ip, puerto, usuario, password, canal = c
                
                # Guardamos un diccionario con toda la data dentro del item del ComboBox
                data_dict = {
                    "id": cid,
                    "nombre": nombre,
                    "tipo": tipo,
                    "ip": ip,
                    "puerto": puerto if puerto else 80, # Por defecto al puerto web estándar
                    "usuario": usuario,
                    "password": password,
                    "canal_defecto": canal
                }
                
                self.combo_camaras.addItem(f"{nombre} ({tipo})", data_dict)
                
            cursor.close()
            conn.close()
            
            # Forzamos la actualización visual de la caja de canales
            self.actualizar_visibilidad_canales()
            
        except Exception as e:
            print("[ERROR] No se pudieron cargar las cámaras en el ComboBox:", e)

    def actualizar_visibilidad_canales(self):
        """Muestra u oculta la caja selectora y lee del SDK cuántos canales reales tiene el NVR."""
        data = self.combo_camaras.currentData()
        if not data:
            return

        if data.get("tipo") == "NVR":
            self.lbl_canal.setVisible(True)
            self.combo_canales.setVisible(True)
            
            # 1. Limpiamos canales anteriores del ComboBox
            self.combo_canales.clear()
            
            # 2. Consultamos al NVR pasando el puerto dinámico de la base de datos (Ej: 84, 80, 8080)
            total_canales = obtener_total_canales(
                ip=data.get("ip"),
                usuario=data.get("usuario"),
                password=data.get("password"),
                puerto=data.get("puerto") # <--- Totalmente dinámico desde la BD
            )
            
            # 3. Llenamos el ComboBox dinámicamente según la respuesta
            if total_canales > 0:
                print(f"[SDK] El NVR {data['nombre']} reporta {total_canales} canales.")
                for i in range(1, total_canales + 1):
                    self.combo_canales.addItem(str(i))
            else:
                # Fallback: Si el equipo está apagado o falla la red, ponemos 16 por defecto
                print(f"[WARNING] No se pudo conectar a la API del NVR {data['nombre']}. Cargando canales por defecto.")
                self.combo_canales.addItems([str(i) for i in range(1, 17)])
            
            # Si tiene un canal configurado por defecto en la BD, lo seleccionamos
            if data.get("canal_defecto"):
                self.combo_canales.setCurrentText(str(data["canal_defecto"]))
        else:
            self.lbl_canal.setVisible(False)
            self.combo_canales.setVisible(False)

    def iniciar_video(self):
        """Obtiene la cámara seleccionada, construye su URL dinámica e inicia el hilo de IA."""
        data = self.combo_camaras.currentData()
        if not data:
            return

        # 1. CONSTRUCCIÓN DINÁMICA DE LA URL RTSP
        if data.get("tipo") == "WEB":
            url = data["url"] # webcam local
        elif data.get("tipo") == "NVR":
            canal_seleccionado = self.combo_canales.currentText()
            # CAMBIO ESTRATÉGICO: Forzamos el puerto de video RTSP estándar a 554 para los NVRs
            url = f"rtsp://{data['usuario']}:{data['password']}@{data['ip']}:554/cam/realmonitor?channel={canal_seleccionado}&subtype=1"
        else: # Cámara IP independiente
            if str(data["ip"]).startswith("rtsp://"):
                url = data["ip"]
            else:
                url = f"rtsp://{data['usuario']}:{data['password']}@{data['ip']}:{data['puerto']}/cam/realmonitor?channel=1&subtype=0"

        # 2. BLOQUEO DE LA INTERFAZ MIENTRAS TRANSMITE
        self.btn_conectar.setEnabled(False)
        self.btn_desconectar.setEnabled(True)
        self.combo_camaras.setEnabled(False)
        self.combo_canales.setEnabled(False)
        self.image_label.setText(f"Iniciando transmisión de video e IA en {data['nombre']}...")

        # 3. INSTANCIACIÓN DEL HILO
        self.thread = VideoThread(camara_id=data["id"], nombre_camara=data["nombre"], rtsp_url=url)
        self.thread.frame_signal.connect(self.actualizar_imagen)
        self.thread.start()

    def detener_video(self):
        """Frena el hilo de video de forma segura y limpia el contenedor."""
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread = None

        self.btn_conectar.setEnabled(True)
        self.btn_desconectar.setEnabled(False)
        self.combo_camaras.setEnabled(True)
        self.combo_canales.setEnabled(True)
        self.image_label.clear()
        self.image_label.setText("Transmisión finalizada. Seleccione otra cámara.")

    def actualizar_imagen(self, q_img):
        if not self.thread:
            return
        pixmap = QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    def showEvent(self, event):
        """Cada vez que el usuario entre a esta pestaña, refresca la lista por si agregó cámaras nuevas en el CRUD."""
        super().showEvent(event)
        if not self.thread or not self.thread.isRunning():
            self.actualizar_lista_camaras()

    def closeEvent(self, event):
        if self.thread:
            self.thread.stop()
        event.accept()