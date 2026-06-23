from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLineEdit
)
from PySide6.QtCore import Qt
from database.db import conectar

class DetectionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título de la sección
        titulo = QLabel("Historial de Logueos y Accesos Faciales")
        titulo.setStyleSheet("font-size: 22px; font-weight: bold; color: #1e293b;")
        layout.addWidget(titulo)

        # Buscador instantáneo con estilo moderno
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("🔍 Filtrar historial por persona o espacio clínico...")
        self.buscador.setStyleSheet("""
            QLineEdit {
                padding: 10px; 
                font-size: 14px; 
                border: 1px solid #cbd5e1; 
                border-radius: 6px; 
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #3b82f6;
            }
        """)
        self.buscador.textChanged.connect(self.filtrar_datos)
        layout.addWidget(self.buscador)

        # Estructura y Estilo de la Tabla para pantallas grandes
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID", "Persona Identificada", "Cámara / Sector", "Fecha y Hora"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        
        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                gridline-color: #e2e8f0;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px;
                font-weight: bold;
                border: 1px solid #e2e8f0;
                color: #475569;
            }
        """)
        layout.addWidget(self.tabla)

        self.cargar_datos()

    def cargar_datos(self):
        self.tabla.setRowCount(0)
        try:
            conn = conectar()
            cursor = conn.cursor()
            query = """
                SELECT d.id, p.nombre, c.nombre, d.fecha_hora 
                FROM detecciones d
                JOIN personas p ON d.persona_id = p.id
                JOIN camaras c ON d.camara_id = c.id
                ORDER BY d.fecha_hora DESC
            """
            cursor.execute(query)
            for fila_idx, fila_datos in enumerate(cursor.fetchall()):
                self.tabla.insertRow(fila_idx)
                for col_idx, dato in enumerate(fila_datos):
                    # Formatear la fecha estéticamente si corresponde
                    if col_idx == 3 and dato is not None:
                        valor = dato.strftime("%Y-%m-%d  |  %I:%M:%S %p")
                    else:
                        valor = str(dato)
                        
                    item = QTableWidgetItem(valor)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.tabla.setItem(fila_idx, col_idx, item)
                    
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"[ERROR] Error al cargar historial en la tabla: {e}")

    def filtrar_datos(self):
        termino = self.buscador.text().lower()
        for f in range(self.tabla.rowCount()):
            match = any(termino in (self.tabla.item(f, c).text().lower() if self.tabla.item(f, c) else "") for c in [1, 2])
            self.tabla.setRowHidden(f, not match)

    def showEvent(self, event):
        super().showEvent(event)
        self.cargar_datos()  # Refresco automático al cambiar de pestaña