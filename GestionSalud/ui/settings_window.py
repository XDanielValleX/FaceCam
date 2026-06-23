from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout
)


class SettingsWindow(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(
            QLabel("Configuración")
        )

        self.setLayout(
            layout
        )