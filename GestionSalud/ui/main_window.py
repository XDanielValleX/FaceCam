from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from ui.sidebar import Sidebar
from ui.persons_window import PersonsWindow   # CRUD de Personas
from ui.camaras_window import CamerasWindow   # type: ignore # CRUD de Cámaras/NVRs
from ui.camara_view import CameraView         # type: ignore # Visualizador de Video en Vivo (NUEVO)

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
        # Índice 0: Dashboard (Panel Principal)
        self.stacked_widget.addWidget(QLabel("Panel Principal (Dashboard) - Próximamente"))

        # Índice 1: Monitoreo (Visualizador de Cámaras en Vivo con Hilos y OpenCV)
        self.vista_monitoreo = CameraView()
        self.stacked_widget.addWidget(self.vista_monitoreo)

        # Índice 2: Gestión de Personas (CRUD con guardado de fotos)
        self.vista_personas = PersonsWindow()
        self.stacked_widget.addWidget(self.vista_personas)

        # Índice 3: Historial (Registro de accesos detectados)
        self.stacked_widget.addWidget(QLabel("Historial de Detecciones - Próximamente"))

        # Índice 4: Configuración del Sistema (CRUD dinámico de Cámaras y NVRs)
        self.vista_cameras = CamerasWindow()
        self.stacked_widget.addWidget(self.vista_cameras)

    def cambiar_vista(self, indice):
        """Cambia la página actual del QStackedWidget al interactuar con el menú."""
        self.stacked_widget.setCurrentIndex(indice)