from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt

class Sidebar(QWidget):
    # Esta señal enviará el índice numérico de la vista que queremos mostrar
    view_changed = Signal(int)

    def __init__(self):
        super().__init__()
        # Ancho fijo para la barra lateral
        self.setFixedWidth(220)
        self.setStyleSheet("background-color: #1e293b; color: #f8fafc;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Título de la aplicación en la barra
        titulo = QLabel("FaceCam\nGestión Salud")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; padding: 25px 10px; background-color: #0f172a;")
        layout.addWidget(titulo)

        # Creación de los botones de navegación
        self.btn_dashboard = self.crear_boton("📊 Dashboard", 0)
        self.btn_camaras = self.crear_boton("📹 Cámaras en Vivo", 1)
        self.btn_personas = self.crear_boton("👥 Personas", 2)
        self.btn_detecciones = self.crear_boton("📋 Detecciones", 3)
        self.btn_config = self.crear_boton("⚙️ Configuración", 4)

        layout.addWidget(self.btn_dashboard)
        layout.addWidget(self.btn_camaras)
        layout.addWidget(self.btn_personas)
        layout.addWidget(self.btn_detecciones)
        layout.addWidget(self.btn_config)

        # Este 'stretch' empuja todos los botones hacia arriba
        layout.addStretch()

    def crear_boton(self, texto, indice):
        btn = QPushButton(texto)
        btn.setStyleSheet("""
            QPushButton {
                padding: 15px 20px;
                text-align: left;
                font-size: 14px;
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #334155;
                border-left: 4px solid #3b82f6;
            }
        """)
        # Al hacer clic, emitimos la señal con el número de página correspondiente
        btn.clicked.connect(lambda: self.view_changed.emit(indice))
        return btn