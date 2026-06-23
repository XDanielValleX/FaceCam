import os
import shutil
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QMessageBox, QInputDialog, QFileDialog)
from database.db import conectar

class PersonsWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # --- 1. Barra de Herramientas (Botones del CRUD + Fotos) ---
        btn_layout = QHBoxLayout()
        
        self.btn_agregar = QPushButton("➕ Agregar Persona")
        self.btn_editar = QPushButton("✏️ Editar Nombre")
        self.btn_eliminar = QPushButton("❌ Eliminar")
        self.btn_foto = QPushButton("📸 Subir Foto")
        self.btn_actualizar = QPushButton("🔄 Actualizar Tabla")

        # Conectar botones a sus respectivas funciones
        self.btn_agregar.clicked.connect(self.agregar_persona)
        self.btn_editar.clicked.connect(self.editar_persona)
        self.btn_eliminar.clicked.connect(self.eliminar_persona)
        self.btn_foto.clicked.connect(self.subir_foto)
        self.btn_actualizar.clicked.connect(self.cargar_datos)

        # Estilos visuales modernos (Colores Tailwind)
        estilo_base = "padding: 8px 12px; font-weight: bold; font-size: 13px; border-radius: 4px; color: white;"
        self.btn_agregar.setStyleSheet(estilo_base + "background-color: #22c55e;")      # Verde
        self.btn_editar.setStyleSheet(estilo_base + "background-color: #3b82f6;")       # Azul
        self.btn_eliminar.setStyleSheet(estilo_base + "background-color: #ef4444;")     # Rojo
        self.btn_foto.setStyleSheet(estilo_base + "background-color: #eab308;")         # Amarillo/Dorado
        self.btn_actualizar.setStyleSheet(estilo_base + "background-color: #64748b;")   # Gris Azulado

        # Agregar botones al contenedor horizontal
        btn_layout.addWidget(self.btn_agregar)
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addWidget(self.btn_foto)
        btn_layout.addWidget(self.btn_actualizar)
        btn_layout.addStretch() # Empuja los botones a la izquierda
        layout.addLayout(btn_layout)

        # --- 2. Configuración de la Tabla (Vista de Datos) ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(2)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre Completo"])
        
        # Ajustes de comportamiento de la tabla
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch) # Nombre estirable
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)                  # Seleccionar fila completa
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)                 # Una sola fila a la vez
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)                    # Celdas de solo lectura
        layout.addWidget(self.tabla)

        # Cargar los datos inmediatamente al abrir la ventana
        self.cargar_datos()

    def obtener_ruta_base(self):
        """Devuelve la ruta raíz del proyecto."""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # === [R] - READ: Leer / Cargar Datos ===
    def cargar_datos(self):
        self.tabla.setRowCount(0)
        conn = None
        cursor = None
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM personas ORDER BY id ASC")
            registros = cursor.fetchall()

            for row_idx, row_data in enumerate(registros):
                self.tabla.insertRow(row_idx)
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
                self.tabla.setItem(row_idx, 1, QTableWidgetItem(row_data[1]))
        except Exception as e:
            QMessageBox.critical(self, "Error de BD", f"No se pudieron cargar los datos:\n{e}")
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # === [C] - CREATE: Agregar Persona ===
    def agregar_persona(self):
        nombre, ok = QInputDialog.getText(self, "Nueva Persona", "Ingresa el nombre completo:")
        if ok and nombre.strip():
            nombre_limpio = nombre.strip()
            conn = None
            cursor = None
            try:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO personas (nombre) VALUES (%s)", (nombre_limpio,))
                conn.commit()

                # Crear la carpeta física para sus fotos
                self.crear_carpeta_persona(nombre_limpio)

                self.cargar_datos()
                QMessageBox.information(self, "Éxito", f"Persona '{nombre_limpio}' agregada correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo agregar a la persona:\n{e}")
            finally:
                if cursor: cursor.close()
                if conn: conn.close()

    # === [U] - UPDATE: Editar Nombre de Persona ===
    def editar_persona(self):
        fila_seleccionada = self.tabla.currentRow()
        if fila_seleccionada >= 0:
            id_persona = self.tabla.item(fila_seleccionada, 0).text()
            nombre_actual = self.tabla.item(fila_seleccionada, 1).text()

            nuevo_nombre, ok = QInputDialog.getText(
                self, "Editar Persona", 
                f"Modificar el nombre de '{nombre_actual}':", 
                text=nombre_actual
            )
            
            if ok and nuevo_nombre.strip() and nuevo_nombre.strip() != nombre_actual:
                nuevo_nombre_limpio = nuevo_nombre.strip()
                conn = None
                cursor = None
                try:
                    conn = conectar()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE personas SET nombre = %s WHERE id = %s", (nuevo_nombre_limpio, id_persona))
                    conn.commit()

                    # Renombrar carpeta física en el sistema de archivos
                    ruta_base = self.obtener_ruta_base()
                    dir_antiguo = os.path.join(ruta_base, "personas", nombre_actual)
                    dir_nuevo = os.path.join(ruta_base, "personas", nuevo_nombre_limpio)
                    
                    if os.path.exists(dir_antiguo):
                        os.rename(dir_antiguo, dir_nuevo)
                    else:
                        os.makedirs(dir_nuevo, exist_ok=True)

                    self.cargar_datos()
                    QMessageBox.information(self, "Éxito", "Nombre actualizado correctamente.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo actualizar el registro:\n{e}")
                finally:
                    if cursor: cursor.close()
                    if conn: conn.close()
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona una persona de la tabla primero.")

    # === [D] - DELETE: Eliminar Persona ===
    def eliminar_persona(self):
        fila_seleccionada = self.tabla.currentRow()
        if fila_seleccionada >= 0:
            id_persona = self.tabla.item(fila_seleccionada, 0).text()
            nombre_persona = self.tabla.item(fila_seleccionada, 1).text()

            respuesta = QMessageBox.question(
                self, "Confirmar Eliminación",
                f"¿Seguro que deseas eliminar a '{nombre_persona}'?\nEsto borrará permanentemente sus fotos y registros.",
                QMessageBox.Yes | QMessageBox.No
            )

            if respuesta == QMessageBox.Yes:
                conn = None
                cursor = None
                try:
                    conn = conectar()
                    cursor = conn.cursor()
                    # 1. Limpiar llave foránea en detecciones
                    cursor.execute("DELETE FROM detecciones WHERE persona_id = %s", (id_persona,))
                    # 2. Eliminar la persona
                    cursor.execute("DELETE FROM personas WHERE id = %s", (id_persona,))
                    conn.commit()
                    
                    # 3. Eliminar la carpeta física de fotos
                    ruta_base = self.obtener_ruta_base()
                    ruta_carpeta = os.path.join(ruta_base, "personas", nombre_persona)
                    if os.path.exists(ruta_carpeta):
                        shutil.rmtree(ruta_carpeta)
                    
                    self.cargar_datos()
                    QMessageBox.information(self, "Éxito", "Persona y archivos eliminados correctamente.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error al eliminar el registro:\n{e}")
                finally:
                    if cursor: cursor.close()
                    if conn: conn.close()
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona una persona de la tabla primero.")

    # === GESTIÓN DE MULTIMEDIA: Subir Fotos ===
    def subir_foto(self):
        fila_seleccionada = self.tabla.currentRow()
        if fila_seleccionada >= 0:
            nombre_persona = self.tabla.item(fila_seleccionada, 1).text()
            
            # Lanzar el buscador de archivos de Windows
            ruta_imagen, _ = QFileDialog.getOpenFileName(
                self, 
                f"Seleccionar foto para {nombre_persona}", 
                "", 
                "Imágenes (*.png *.jpg *.jpeg)"
            )

            if ruta_imagen:
                try:
                    ruta_base = self.obtener_ruta_base()
                    carpeta_destino = os.path.join(ruta_base, "personas", nombre_persona)
                    
                    # Asegurar la existencia de la carpeta destino
                    os.makedirs(carpeta_destino, exist_ok=True)
                        
                    # Extraer el nombre original del archivo y copiarlo
                    nombre_archivo = os.path.basename(ruta_imagen)
                    ruta_final = os.path.join(carpeta_destino, nombre_archivo)
                    
                    shutil.copy(ruta_imagen, ruta_final)
                    QMessageBox.information(self, "Éxito", f"Foto añadida correctamente al perfil de {nombre_persona}.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo guardar la imagen:\n{e}")
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona una persona de la tabla primero.")

    def crear_carpeta_persona(self, nombre):
        """Crea un directorio exclusivo para el reconocimiento de la persona."""
        ruta_base = self.obtener_ruta_base()
        ruta_carpeta = os.path.join(ruta_base, "personas", nombre)
        os.makedirs(ruta_carpeta, exist_ok=True)