def obtener_estilos():

    return """
    QWidget {
        background-color: #1E1E1E;
        color: white;
        font-size: 11pt;
        font-family: Segoe UI;
    }

    QMainWindow {
        background-color: #1E1E1E;
    }

    /* ==========================
       BOTONES
    ========================== */

    QPushButton {

        background-color: #0078D7;

        border: none;

        border-radius: 8px;

        padding: 10px;

        color: white;

        font-weight: bold;
    }

    QPushButton:hover {

        background-color: #2893FF;
    }

    QPushButton:pressed {

        background-color: #005EA8;
    }

    /* ==========================
       TABLAS
    ========================== */

    QTableWidget {

        background-color: #252526;

        border: 1px solid #3C3C3C;

        gridline-color: #3C3C3C;
    }

    QHeaderView::section {

        background-color: #333333;

        color: white;

        padding: 5px;

        border: 1px solid #444444;
    }

    /* ==========================
       CAJAS DE TEXTO
    ========================== */

    QLineEdit {

        background-color: #2D2D30;

        border: 1px solid #555555;

        border-radius: 5px;

        padding: 8px;
    }

    QLineEdit:focus {

        border: 2px solid #0078D7;
    }

    /* ==========================
       COMBOBOX
    ========================== */

    QComboBox {

        background-color: #2D2D30;

        border: 1px solid #555555;

        border-radius: 5px;

        padding: 6px;
    }

    QComboBox::drop-down {

        border: none;
    }

    /* ==========================
       LABELS
    ========================== */

    QLabel {

        color: white;
    }

    /* ==========================
       GROUP BOX
    ========================== */

    QGroupBox {

        border: 1px solid #555555;

        border-radius: 8px;

        margin-top: 10px;

        padding-top: 15px;

        font-weight: bold;
    }

    QGroupBox::title {

        subcontrol-origin: margin;

        left: 10px;

        padding: 0px 5px;
    }

    /* ==========================
       MENÚS
    ========================== */

    QMenuBar {

        background-color: #252526;
    }

    QMenuBar::item {

        background-color: transparent;

        padding: 8px 15px;
    }

    QMenuBar::item:selected {

        background-color: #0078D7;
    }

    QMenu {

        background-color: #252526;
    }

    QMenu::item:selected {

        background-color: #0078D7;
    }

    /* ==========================
       BARRA DE ESTADO
    ========================== */

    QStatusBar {

        background-color: #252526;
    }

    /* ==========================
       SCROLL
    ========================== */

    QScrollBar:vertical {

        background-color: #252526;

        width: 12px;
    }

    QScrollBar::handle:vertical {

        background-color: #555555;

        border-radius: 5px;
    }

    QScrollBar::handle:vertical:hover {

        background-color: #777777;
    }
    """