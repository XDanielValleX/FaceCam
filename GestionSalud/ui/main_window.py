from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Qt

# Importaciones de la barra lateral y vistas existentes
from ui.sidebar import Sidebar
from ui.camara_view import CameraView         # Visualizador de Video en Vivo
from ui.persons_window import PersonsWindow   # CRUD de Personas
from ui.camaras_window import CamerasWindow   # CRUD de Cámaras/NVRs

# --- NUEVAS IMPORTACIONES RE REALES ---
from ui.dashboard_window import DashboardWindow
from ui.detections_window import DetectionsWindow  # (Asegúrate de que el archivo se llame detections_window.py)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaceCam - Sistema de Reconocimiento Facial")
        self.resize(1200, 800) 

        # Widget central y layout horizontal principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Quitamos los márgenes para que la sidebar toque los bordes de la ventana
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Instanciamos y agregamos la Barra Lateral (Sidebar)
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        # 2. Instanciamos y agregamos el contenedor de páginas (QStackedWidget)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #f1f5f9; color: #0f172a;")
        main_layout.addWidget(self.stacked_widget)

        # Conectamos la señal de la barra lateral para cambiar de vista de forma dinámica
        self.sidebar.view_changed.connect(self.cambiar_vista)

        # Cargamos los módulos correspondientes en cada pestaña
        self.configurar_vistas()

    def configurar_vistas(self):
        # Índice 0: Dashboard (Panel Principal Real)
        self.vista_dashboard = DashboardWindow()
        self.stacked_widget.addWidget(self.vista_dashboard)

        # Índice 1: Monitoreo (Visualizador de Cámaras en Vivo)
        self.vista_monitoreo = CameraView()
        self.stacked_widget.addWidget(self.vista_monitoreo)

        # Índice 2: Gestión de Personas (CRUD con fotos)
        self.vista_personas = PersonsWindow()
        self.stacked_widget.addWidget(self.vista_personas)

        # Índice 3: Historial (Registro de accesos detectados Real)
        self.vista_detecciones = DetectionsWindow()
        self.stacked_widget.addWidget(self.vista_detecciones)

        # Índice 4: Configuración del Sistema (CRUD de Cámaras y NVRs)
        self.vista_cameras = CamerasWindow()
        self.stacked_widget.addWidget(self.vista_cameras)

    def cambiar_vista(self, indice):
        """Cambia la página actual del QStackedWidget al interactuar con el menú."""
        self.stacked_widget.setCurrentIndex(indice)