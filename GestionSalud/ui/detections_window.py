from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout
)


class DetectionsWindow(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(
            QLabel("Detecciones")
        )

        self.setLayout(
            layout
        )