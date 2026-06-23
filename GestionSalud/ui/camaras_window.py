from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QMessageBox, QDialog, QFormLayout, QLineEdit, 
                               QComboBox, QSpinBox)
from PySide6.QtCore import Qt
from database.db import conectar

# ==========================================
# FORMULARIO EMERGENTE PARA CREAR/EDITAR
# ==========================================
class CameraFormDialog(QDialog):
    def __init__(self, parent=None, datos_camara=None):
        super().__init__(parent)
        self.setWindowTitle("Formulario de Cámara / NVR")
        self.resize(400, 350)
        self.datos = datos_camara # Si trae datos, es Edición. Si es None, es Creación.

        layout = QFormLayout(self)

        # Campos del formulario
        self.input_nombre = QLineEdit()
        self.input_ubicacion = QLineEdit()
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["IP", "NVR"])
        
        self.input_ip = QLineEdit()
        
        self.spin_puerto = QSpinBox()
        self.spin_puerto.setRange(1, 65535)
        self.spin_puerto.setValue(80) # Puerto inicial estándar (Cámaras IP suelen usar 554, NVRs usan 80/84 para la API)
        
        self.input_usuario = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        
        self.spin_canal = QSpinBox()
        self.spin_canal.setRange(1, 256)

        # Añadir al layout
        layout.addRow("Nombre descriptivo:", self.input_nombre)
        layout.addRow("Ubicación:", self.input_ubicacion)
        layout.addRow("Tipo de Dispositivo:", self.combo_tipo)
        layout.addRow("Dirección IP:", self.input_ip)
        layout.addRow("Puerto (Web / RTSP):", self.spin_puerto)
        layout.addRow("Usuario:", self.input_usuario)
        layout.addRow("Contraseña:", self.input_password)
        layout.addRow("Canal (NVR):", self.spin_canal)

        # Botones de Guardar/Cancelar
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("💾 Guardar")
        self.btn_cancelar = QPushButton("❌ Cancelar")
        
        self.btn_guardar.setStyleSheet("background-color: #22c55e; color: white; padding: 8px; font-weight: bold;")
        self.btn_cancelar.setStyleSheet("background-color: #64748b; color: white; padding: 8px; font-weight: bold;")
        
        self.btn_guardar.clicked.connect(self.accept)
        self.btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addRow(btn_layout)

        # Si es edición, rellenar los campos
        if self.datos:
            self.input_nombre.setText(self.datos[1])
            self.input_ubicacion.setText(self.datos[2])
            self.combo_tipo.setCurrentText(self.datos[3])
            self.input_ip.setText(self.datos[4])
            self.spin_puerto.setValue(int(self.datos[5]) if self.datos[5] else 80)
            self.input_usuario.setText(self.datos[6])
            self.input_password.setText(self.datos[7])
            self.spin_canal.setValue(int(self.datos[8]) if self.datos[8] else 1)

    def get_data(self):
        return {
            "nombre": self.input_nombre.text().strip(),
            "ubicacion": self.input_ubicacion.text().strip(),
            "tipo": self.combo_tipo.currentText(),
            "ip": self.input_ip.text().strip(),
            "puerto": self.spin_puerto.value(),
            "usuario": self.input_usuario.text().strip(),
            "password": self.input_password.text().strip(),
            "canal": self.spin_canal.value()
        }

# ==========================================
# VENTANA PRINCIPAL DEL CRUD DE CÁMARAS
# ==========================================
class CamerasWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # --- Botones ---
        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("➕ Nueva Cámara/NVR")
        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_eliminar = QPushButton("❌ Eliminar")
        self.btn_actualizar = QPushButton("🔄 Actualizar")

        estilo_base = "padding: 8px; font-weight: bold; font-size: 13px; color: white; border-radius: 4px;"
        self.btn_agregar.setStyleSheet(estilo_base + "background-color: #22c55e;")
        self.btn_editar.setStyleSheet(estilo_base + "background-color: #3b82f6;")
        self.btn_eliminar.setStyleSheet(estilo_base + "background-color: #ef4444;")
        self.btn_actualizar.setStyleSheet(estilo_base + "background-color: #64748b;")

        self.btn_agregar.clicked.connect(self.agregar_camara)
        self.btn_editar.clicked.connect(self.editar_camara)
        self.btn_eliminar.clicked.connect(self.eliminar_camara)
        self.btn_actualizar.clicked.connect(self.cargar_datos)

        btn_layout.addWidget(self.btn_agregar)
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addWidget(self.btn_actualizar)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # --- Tabla ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Tipo", "IP", "Puerto", "Canal", "Ubicación"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla)

        self.cargar_datos()

    def cargar_datos(self):
        self.tabla.setRowCount(0)
        conn, cursor = None, None
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, ubicacion, tipo, ip, puerto, usuario, password, canal FROM camaras ORDER BY id")
            self.registros_completos = cursor.fetchall() # Guardamos en memoria para usar en edición

            for row_idx, row_data in enumerate(self.registros_completos):
                self.tabla.insertRow(row_idx)
                # Mostrar solo datos no sensibles en la tabla
                columnas_mostrar = [0, 1, 3, 4, 5, 8, 2] # Índices de: ID, Nombre, Tipo, IP, Puerto, Canal, Ubicacion
                for col_idx, data_idx in enumerate(columnas_mostrar):
                    self.tabla.setItem(row_idx, col_idx, QTableWidgetItem(str(row_data[data_idx])))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar las cámaras:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def agregar_camara(self):
        dialogo = CameraFormDialog(self)
        if dialogo.exec() == QDialog.Accepted:
            data = dialogo.get_data()
            conn, cursor = None, None
            try:
                conn = conectar()
                cursor = conn.cursor()
                query = """INSERT INTO camaras (nombre, ubicacion, tipo, ip, puerto, usuario, password, canal) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                valores = (data['nombre'], data['ubicacion'], data['tipo'], data['ip'], 
                           data['puerto'], data['usuario'], data['password'], data['canal'])
                cursor.execute(query, valores)
                conn.commit()
                self.cargar_datos()
                QMessageBox.information(self, "Éxito", "Dispositivo agregado correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Fallo al guardar:\n{e}")
            finally:
                if cursor: cursor.close()
                if conn: conn.close()

    def editar_camara(self):
        fila = self.tabla.currentRow()
        if fila >= 0:
            # Recuperar todos los datos (incluyendo passwords) desde nuestra variable en memoria
            datos_actuales = self.registros_completos[fila]
            id_camara = datos_actuales[0]

            dialogo = CameraFormDialog(self, datos_camara=datos_actuales)
            if dialogo.exec() == QDialog.Accepted:
                data = dialogo.get_data()
                conn, cursor = None, None
                try:
                    conn = conectar()
                    cursor = conn.cursor()
                    query = """UPDATE camaras SET nombre=%s, ubicacion=%s, tipo=%s, ip=%s, 
                               puerto=%s, usuario=%s, password=%s, canal=%s WHERE id=%s"""
                    valores = (data['nombre'], data['ubicacion'], data['tipo'], data['ip'], 
                               data['puerto'], data['usuario'], data['password'], data['canal'], id_camara)
                    cursor.execute(query, valores)
                    conn.commit()
                    self.cargar_datos()
                    QMessageBox.information(self, "Éxito", "Dispositivo actualizado.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Fallo al actualizar:\n{e}")
                finally:
                    if cursor: cursor.close()
                    if conn: conn.close()
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona una cámara primero.")

    def eliminar_camara(self):
        fila = self.tabla.currentRow()
        if fila >= 0:
            id_camara = self.tabla.item(fila, 0).text()
            nombre = self.tabla.item(fila, 1).text()

            if QMessageBox.question(self, "Confirmar", f"¿Eliminar '{nombre}'?", 
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                conn, cursor = None, None
                try:
                    conn = conectar()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM camaras WHERE id = %s", (id_camara,))
                    conn.commit()
                    self.cargar_datos()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Fallo al eliminar:\n{e}")
                finally:
                    if cursor: cursor.close()
                    if conn: conn.close()
        else:
            QMessageBox.warning(self, "Advertencia", "Selecciona una cámara primero.")