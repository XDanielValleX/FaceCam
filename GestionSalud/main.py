from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()

    # Abrir la aplicación directamente en pantalla completa maximizada
    ventana.showMaximized()

    # NOTA: Si prefieres el modo Kiosko absoluto (que oculte también la barra de tareas),
    # puedes comentar la línea de arriba y descomentar la de abajo:
    # ventana.showFullScreen()

    sys.exit(app.exec())