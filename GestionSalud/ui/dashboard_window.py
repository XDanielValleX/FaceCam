from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from database.db import conectar

class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título Principal
        titulo = QLabel("Panel de Control General (Dashboard)")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a;")
        layout.addWidget(titulo)

        # Contenedor de Tarjetas KPI
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)

        self.card_personas = self.crear_tarjeta("Personas Registradas", "0", "#3b82f6")
        self.card_camaras = self.crear_tarjeta("Cámaras / Canales", "0", "#10b981")
        self.card_detecciones = self.crear_tarjeta("Detecciones de Hoy", "0", "#f59e0b")

        kpi_layout.addWidget(self.card_personas)
        kpi_layout.addWidget(self.card_camaras)
        kpi_layout.addWidget(self.card_detecciones)
        layout.addLayout(kpi_layout)

        # Espacio inferior de bienvenida para rellenar armoniosamente la pantalla completa
        bienvenida = QLabel("Sistema Inteligente FaceCam en ejecución activa.\nMonitoreando accesos biométricos y seguridad perimetral.")
        bienvenida.setAlignment(Qt.AlignCenter)
        bienvenida.setStyleSheet("""
            QLabel {
                color: #64748b; 
                font-size: 15px; 
                font-style: italic; 
                border-top: 1px dashed #e2e8f0;
                padding-top: 40px;
            }
        """)
        layout.addWidget(bienvenida, stretch=1)

        self.actualizar_metricas()

    def crear_tarjeta(self, titulo, valor_inicial, color_borde):
        marco = QFrame()
        marco.setStyleSheet(f"""
            QFrame {{
                background-color: white; 
                border-radius: 8px; 
                border-left: 6px solid {color_borde};
                border-top: 1px solid #f1f5f9;
                border-right: 1px solid #f1f5f9;
                border-bottom: 1px solid #f1f5f9;
            }}
        """)
        lay_card = QVBoxLayout(marco)
        lay_card.setContentsMargins(15, 15, 15, 15)
        
        lbl_tit = QLabel(titulo)
        lbl_tit.setStyleSheet("color: #64748b; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        
        lbl_val = QLabel(valor_inicial)
        lbl_val.setStyleSheet("color: #1e293b; font-size: 32px; font-weight: bold; border: none; background: transparent;")
        lbl_val.setObjectName("valor")
        
        lay_card.addWidget(lbl_tit)
        lay_card.addWidget(lbl_val)
        return marco

    def actualizar_metricas(self):
        try:
            conn = conectar()
            cursor = conn.cursor()

            # Métrica 1: Personas Totales
            cursor.execute("SELECT COUNT(*) FROM personas")
            self.card_personas.findChild(QLabel, "valor").setText(str(cursor.fetchone()[0]))

            # Métrica 2: Cámaras/Canales Totales
            cursor.execute("SELECT COUNT(*) FROM camaras")
            self.card_camaras.findChild(QLabel, "valor").setText(str(cursor.fetchone()[0]))

            # Métrica 3: Detecciones hoy (Usa el casteo de Postgres compatible con zonas horarias)
            cursor.execute("SELECT COUNT(*) FROM detecciones WHERE fecha_hora::date = CURRENT_DATE")
            self.card_detecciones.findChild(QLabel, "valor").setText(str(cursor.fetchone()[0]))

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"[ERROR] Error al actualizar métricas del Dashboard: {e}")

    def showEvent(self, event):
        super().showEvent(event)
        self.actualizar_metricas() # Refresco automático de contadores al entrar a la vista principal