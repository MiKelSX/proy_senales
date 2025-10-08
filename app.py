import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QSlider, 
                             QHBoxLayout, QFrame, QGraphicsDropShadowEffect, 
                             QScrollArea, QGridLayout, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont, QColor, QPalette
import pyqtgraph.opengl as gl
from PIL import Image
import pyqtgraph as pg

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.default_color = QColor(100, 120, 255)
        self.hover_color = QColor(130, 150, 255)
        self._bg_color = self.default_color
        self.setup_style()
        
    def setup_style(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(100, 120, 255, 100))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        self.update_style()
        
    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self._bg_color.name()}, 
                    stop:1 {self._bg_color.lighter(120).name()});
                color: white;
                border: none;
                border-radius: 20px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.hover_color.name()}, 
                    stop:1 {self.hover_color.lighter(120).name()});
            }}
            QPushButton:pressed {{
                padding: 17px 30px 13px 30px;
            }}
        """)
    
    def get_bg_color(self):
        return self._bg_color
    
    def set_bg_color(self, color):
        self._bg_color = color
        self.update_style()
    
    bg_color = pyqtProperty(QColor, get_bg_color, set_bg_color)

class ToggleButton(QPushButton):
    def __init__(self, text_on, text_off, icon_on="▶", icon_off="⏸", parent=None):
        super().__init__(parent)
        self.text_on = text_on
        self.text_off = text_off
        self.icon_on = icon_on
        self.icon_off = icon_off
        self.is_active = False
        self.update_state()
        
    def update_state(self):
        if self.is_active:
            text = f"{self.icon_off} {self.text_off}"
            color1 = "#FF6B9D"
            color2 = "#FFA06B"
        else:
            text = f"{self.icon_on} {self.text_on}"
            color1 = "#6478FF"
            color2 = "#8296FF"
            
        self.setText(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color1}, stop:1 {color2});
                color: white;
                border: none;
                border-radius: 18px;
                padding: 12px 25px;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color1}DD, stop:1 {color2}DD);
            }}
            QPushButton:pressed {{
                padding: 14px 25px 10px 25px;
            }}
        """)
        
    def toggle(self):
        self.is_active = not self.is_active
        self.update_state()
        return self.is_active

class ModernSlider(QWidget):
    def __init__(self, label_text, min_val, max_val, default_val, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(label_text)
        self.label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 13px;
                font-weight: 500;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        self.value_label = QLabel(str(default_val))
        self.value_label.setStyleSheet("""
            QLabel {
                color: #6478FF;
                font-size: 15px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        header = QHBoxLayout()
        header.addWidget(self.label)
        header.addStretch()
        header.addWidget(self.value_label)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setValue(default_val)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #2A2A3E;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6478FF, stop:1 #8296FF);
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
                border: 2px solid #FFFFFF;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8296FF, stop:1 #A0B4FF);
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6478FF, stop:1 #8296FF);
                border-radius: 3px;
            }
        """)
        
        self.slider.valueChanged.connect(lambda v: self.value_label.setText(str(v)))
        
        layout.addLayout(header)
        layout.addWidget(self.slider)
        self.setLayout(layout)

class ResultsWindow(QMainWindow):
    def __init__(self, image_data, parent=None):
        super().__init__(parent)
        self.image_data = image_data
        self.init_ui()
        self.calculate_all()
        
    def init_ui(self):
        self.setWindowTitle("📊 Análisis Matemático Completo")
        self.setGeometry(200, 150, 1000, 700)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(15, 15, 25))
        self.setPalette(palette)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1E1E2E;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6478FF, stop:1 #8296FF);
                border-radius: 6px;
                min-height: 30px;
            }
        """)
        
        content = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Título principal
        title = QLabel("⚡ ANÁLISIS ESPECTRAL Y TRANSFORMADAS")
        title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 32px;
                font-weight: 800;
                font-family: 'Segoe UI', sans-serif;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6478FF, stop:1 #8296FF);
                border-radius: 20px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Contenedor de resultados
        self.results_layout = QGridLayout()
        self.results_layout.setSpacing(20)
        
        content.setLayout(main_layout)
        scroll.setWidget(content)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        central.setLayout(layout)
        
    def create_result_card(self, title, symbol, value, unit="", description=""):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E1E2E, stop:1 #2A2A3E);
                border-radius: 20px;
                border: 2px solid #6478FF;
                padding: 20px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(100, 120, 255, 80))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #A0B0FF;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        symbol_label = QLabel(symbol)
        symbol_label.setStyleSheet("""
            QLabel {
                color: #6478FF;
                font-size: 36px;
                font-weight: 700;
                font-family: 'Times New Roman', serif;
            }
        """)
        symbol_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(f"{value}")
        value_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: 700;
                font-family: 'Consolas', monospace;
            }
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setWordWrap(True)
        
        if unit:
            unit_label = QLabel(unit)
            unit_label.setStyleSheet("""
                QLabel {
                    color: #8296FF;
                    font-size: 16px;
                    font-weight: 500;
                    font-family: 'Segoe UI', sans-serif;
                }
            """)
            unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                QLabel {
                    color: #7080A0;
                    font-size: 11px;
                    font-family: 'Segoe UI', sans-serif;
                    padding-top: 10px;
                }
            """)
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(symbol_label)
        layout.addWidget(value_label)
        if unit:
            layout.addWidget(unit_label)
        if description:
            layout.addWidget(desc_label)
        layout.addStretch()
        
        card.setLayout(layout)
        return card
        
    def calculate_all(self):
        gray = np.mean(self.image_data, axis=2)
        h, w = gray.shape
        
        # FFT 2D
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shift)
        phase = np.angle(fft_shift)
        power_spectrum = magnitude ** 2
        
        # Cálculos
        mean_mag = np.mean(magnitude)
        max_mag = np.max(magnitude)
        min_mag = np.min(magnitude)
        std_mag = np.std(magnitude)
        total_energy = np.sum(power_spectrum)
        mean_phase = np.mean(phase)
        
        # Frecuencias dominantes
        flat_mag = magnitude.flatten()
        top_5_indices = np.argpartition(flat_mag, -5)[-5:]
        dominant_freqs = flat_mag[top_5_indices]
        
        # Entropía espectral
        normalized_power = power_spectrum / np.sum(power_spectrum)
        spectral_entropy = -np.sum(normalized_power * np.log2(normalized_power + 1e-12))
        
        # Centroide espectral
        freq_x = np.fft.fftfreq(w)
        freq_y = np.fft.fftfreq(h)
        fx_grid, fy_grid = np.meshgrid(freq_x, freq_y)
        centroid_x = np.sum(fx_grid * power_spectrum) / np.sum(power_spectrum)
        centroid_y = np.sum(fy_grid * power_spectrum) / np.sum(power_spectrum)
        
        # Ancho de banda espectral
        bandwidth = np.sqrt(np.sum(((fx_grid - centroid_x)**2 + (fy_grid - centroid_y)**2) * power_spectrum) / np.sum(power_spectrum))
        
        # Razón señal-ruido (estimado)
        signal_power = np.max(power_spectrum)
        noise_power = np.median(power_spectrum)
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 0
        
        # Complejidad espectral
        spectral_flatness = np.exp(np.mean(np.log(magnitude + 1e-12))) / (np.mean(magnitude) + 1e-12)
        
        # Contenedor principal
        main_layout = self.centralWidget().findChild(QScrollArea).widget().layout()
        
        # Grid de resultados
        grid_container = QWidget()
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Fila 1: Transformada de Fourier
        grid.addWidget(self.create_result_card(
            "Transformada Fourier 2D",
            "ℱ{f(x,y)}",
            f"F(u,v) = ∫∫ f(x,y)e^(-2πi(ux+vy))dxdy",
            "",
            f"Componentes totales: {h}×{w} = {h*w:,}"
        ), 0, 0)
        
        grid.addWidget(self.create_result_card(
            "Dimensiones del espectro",
            "N × M",
            f"{h} × {w}",
            "píxeles",
            "Resolución del análisis frecuencial"
        ), 0, 1)
        
        # Fila 2: Magnitud
        grid.addWidget(self.create_result_card(
            "Magnitud promedio",
            "μ(|F|)",
            f"{mean_mag:.4e}",
            "",
            "Media aritmética del espectro"
        ), 1, 0)
        
        grid.addWidget(self.create_result_card(
            "Magnitud máxima",
            "max(|F|)",
            f"{max_mag:.4e}",
            "",
            "Componente de mayor amplitud"
        ), 1, 1)
        
        grid.addWidget(self.create_result_card(
            "Desviación estándar",
            "σ(|F|)",
            f"{std_mag:.4e}",
            "",
            "Dispersión del espectro"
        ), 1, 2)
        
        # Fila 3: Energía y Potencia
        grid.addWidget(self.create_result_card(
            "Energía total",
            "E = Σ|F|²",
            f"{total_energy:.4e}",
            "J",
            "Parseval: energía conservada"
        ), 2, 0)
        
        grid.addWidget(self.create_result_card(
            "Potencia espectral",
            "P(u,v)",
            f"{np.mean(power_spectrum):.4e}",
            "W/Hz²",
            "Densidad espectral de potencia"
        ), 2, 1)
        
        grid.addWidget(self.create_result_card(
            "Relación señal/ruido",
            "SNR",
            f"{snr:.2f}",
            "dB",
            "Calidad de la señal"
        ), 2, 2)
        
        # Fila 4: Fase y características
        grid.addWidget(self.create_result_card(
            "Fase promedio",
            "⟨φ⟩",
            f"{mean_phase:.4f}",
            "rad",
            "Ángulo promedio del espectro"
        ), 3, 0)
        
        grid.addWidget(self.create_result_card(
            "Entropía espectral",
            "H = -Σp·log₂(p)",
            f"{spectral_entropy:.4f}",
            "bits",
            "Complejidad de la información"
        ), 3, 1)
        
        grid.addWidget(self.create_result_card(
            "Planicidad espectral",
            "SFM",
            f"{spectral_flatness:.4f}",
            "",
            "Razón entre media geom./arit."
        ), 3, 2)
        
        # Fila 5: Centroide y ancho de banda
        grid.addWidget(self.create_result_card(
            "Centroide X",
            "c_x",
            f"{centroid_x:.6f}",
            "Hz",
            "Centro de masa espectral en X"
        ), 4, 0)
        
        grid.addWidget(self.create_result_card(
            "Centroide Y",
            "c_y",
            f"{centroid_y:.6f}",
            "Hz",
            "Centro de masa espectral en Y"
        ), 4, 1)
        
        grid.addWidget(self.create_result_card(
            "Ancho de banda",
            "BW = √(Σf²·P/ΣP)",
            f"{bandwidth:.6f}",
            "Hz",
            "Dispersión frecuencial"
        ), 4, 2)
        
        # Fila 6: Frecuencias dominantes
        dom_freq_text = "\n".join([f"f₍{i+1}₎ = {freq:.2e}" for i, freq in enumerate(sorted(dominant_freqs, reverse=True))])
        grid.addWidget(self.create_result_card(
            "Frecuencias dominantes",
            "f_dominant",
            dom_freq_text,
            "",
            "Top 5 componentes espectrales"
        ), 5, 0, 1, 3)
        
        grid_container.setLayout(grid)
        main_layout.addWidget(grid_container)
        
        # Fórmulas adicionales
        formulas_frame = QFrame()
        formulas_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2A1E3E, stop:1 #3E2A4E);
                border-radius: 20px;
                border: 2px solid #8296FF;
                padding: 25px;
            }
        """)
        
        formulas_layout = QVBoxLayout()
        
        formula_title = QLabel("📐 ECUACIONES FUNDAMENTALES")
        formula_title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 20px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
                padding-bottom: 15px;
            }
        """)
        
        formulas = [
            ("Transformada Inversa:", "f(x,y) = ∫∫ F(u,v)e^(2πi(ux+vy))dudv"),
            ("Teorema de Parseval:", "∫∫|f(x,y)|²dxdy = ∫∫|F(u,v)|²dudv"),
            ("Magnitud:", "|F(u,v)| = √[Re²(F) + Im²(F)]"),
            ("Fase:", "φ(u,v) = arctan[Im(F)/Re(F)]"),
            ("Potencia:", "P(u,v) = |F(u,v)|²"),
            ("Energía:", "E = ΣΣ|F(u,v)|²"),
        ]
        
        formulas_layout.addWidget(formula_title)
        
        for name, formula in formulas:
            formula_card = QHBoxLayout()
            
            name_label = QLabel(name)
            name_label.setStyleSheet("""
                QLabel {
                    color: #A0B0FF;
                    font-size: 14px;
                    font-weight: 600;
                    font-family: 'Segoe UI', sans-serif;
                }
            """)
            
            formula_label = QLabel(formula)
            formula_label.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    font-size: 16px;
                    font-weight: 500;
                    font-family: 'Cambria Math', 'Times New Roman', serif;
                    padding: 8px 15px;
                    background: #1E1E2E;
                    border-radius: 10px;
                }
            """)
            
            formula_card.addWidget(name_label)
            formula_card.addWidget(formula_label, stretch=1)
            formulas_layout.addLayout(formula_card)
        
        formulas_frame.setLayout(formulas_layout)
        main_layout.addWidget(formulas_frame)

class WaveVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_data = None
        self.wave_mesh = None
        self.wave_lines = []
        self.rotation_angle = 0
        self.wave_offset = 0
        self.panel_visible = True
        self.rotation_active = True
        self.wave_animation_active = False
        self.line_mode = 0  # 0: sin líneas, 1: X, 2: Y, 3: X+Y
        self.results_window = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Wave Visualizer 3D - FFT Analysis")
        self.setGeometry(100, 100, 1400, 900)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        self.setPalette(palette)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Panel de control lateral con scroll
        self.control_panel = QFrame()
        self.control_panel.setMinimumWidth(320)
        self.control_panel.setMaximumWidth(380)
        self.control_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E1E2E, stop:1 #2A2A3E);
                border: none;
            }
        """)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #1E1E2E;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #6478FF;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #8296FF;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        scroll_content = QWidget()
        control_layout = QVBoxLayout()
        control_layout.setSpacing(20)
        control_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("🌊 Wave Visualizer")
        title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 26px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
                padding: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Botón de carga
        self.load_btn = AnimatedButton("📁 Cargar Imagen")
        self.load_btn.clicked.connect(self.load_image)
        
        # Info de imagen
        self.info_label = QLabel("No hay imagen cargada")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #A0A0B0;
                font-size: 12px;
                font-family: 'Segoe UI', sans-serif;
                background: #2A2A3E;
                padding: 12px;
                border-radius: 12px;
            }
        """)
        self.info_label.setWordWrap(True)
        
        # Sección de visualización
        viz_label = QLabel("📊 VISUALIZACIÓN")
        viz_label.setStyleSheet("""
            QLabel {
                color: #6478FF;
                font-size: 14px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
                padding: 5px 0px;
            }
        """)
        
        self.amplitude_slider = ModernSlider("Amplitud", 1, 100, 20)
        self.resolution_slider = ModernSlider("Resolución", 10, 200, 50)
        
        self.amplitude_slider.slider.valueChanged.connect(self.update_visualization)
        self.resolution_slider.slider.valueChanged.connect(self.update_visualization)
        
        # Selector de tipo de líneas
        lines_container = QWidget()
        lines_layout = QVBoxLayout()
        lines_layout.setSpacing(8)
        
        lines_title = QLabel("Tipo de líneas")
        lines_title.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 13px;
                font-weight: 500;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        self.line_mode_combo = QComboBox()
        self.line_mode_combo.addItems(["Sin líneas", "Líneas X", "Líneas Y", "Líneas X + Y"])
        self.line_mode_combo.setStyleSheet("""
            QComboBox {
                background: #2A2A3E;
                color: #E0E0E0;
                border: 2px solid #6478FF;
                border-radius: 12px;
                padding: 10px 15px;
                font-size: 13px;
                font-weight: 500;
                font-family: 'Segoe UI', sans-serif;
            }
            QComboBox:hover {
                background: #3A3A4E;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #6478FF;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background: #2A2A3E;
                color: #E0E0E0;
                selection-background-color: #6478FF;
                border: 2px solid #6478FF;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        self.line_mode_combo.currentIndexChanged.connect(self.change_line_mode)
        
        lines_layout.addWidget(lines_title)
        lines_layout.addWidget(self.line_mode_combo)
        lines_container.setLayout(lines_layout)
        
        # Sección de rotación
        rot_label = QLabel("🔄 ROTACIÓN")
        rot_label.setStyleSheet(viz_label.styleSheet())
        
        self.rotation_toggle = ToggleButton("Pausar", "Reanudar", "⏸", "▶")
        self.rotation_toggle.is_active = True
        self.rotation_toggle.update_state()
        self.rotation_toggle.clicked.connect(self.toggle_rotation)
        
        self.rotation_speed_slider = ModernSlider("Velocidad Rotación", 0, 20, 2)
        
        # Sección de animación de ondas
        wave_label = QLabel("〰️ ANIMACIÓN DE ONDAS")
        wave_label.setStyleSheet(viz_label.styleSheet())
        
        self.wave_toggle = ToggleButton("Activar", "Desactivar", "▶", "⏸")
        self.wave_toggle.clicked.connect(self.toggle_wave_animation)
        
        self.wave_speed_slider = ModernSlider("Velocidad Ondas", 1, 20, 5)
        self.wave_direction_slider = ModernSlider("Dirección (X↔Y)", 0, 1, 0)
        
        # Botón de resultados matemáticos
        self.results_btn = AnimatedButton("🧮 Ver Resultados")
        self.results_btn.clicked.connect(self.show_results_window)
        self.results_btn.setEnabled(False)
        
        # Botón de análisis FFT
        self.fft_btn = AnimatedButton("⚡ Análisis FFT")
        self.fft_btn.clicked.connect(self.show_fft_analysis)
        self.fft_btn.setEnabled(False)
        
        control_layout.addWidget(title)
        control_layout.addWidget(self.load_btn)
        control_layout.addWidget(self.info_label)
        control_layout.addWidget(viz_label)
        control_layout.addWidget(self.amplitude_slider)
        control_layout.addWidget(self.resolution_slider)
        control_layout.addWidget(lines_container)
        control_layout.addWidget(rot_label)
        control_layout.addWidget(self.rotation_toggle)
        control_layout.addWidget(self.rotation_speed_slider)
        control_layout.addWidget(wave_label)
        control_layout.addWidget(self.wave_toggle)
        control_layout.addWidget(self.wave_speed_slider)
        control_layout.addWidget(self.wave_direction_slider)
        control_layout.addWidget(self.results_btn)
        control_layout.addWidget(self.fft_btn)
        control_layout.addStretch()
        
        scroll_content.setLayout(control_layout)
        scroll_area.setWidget(scroll_content)
        
        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)
        self.control_panel.setLayout(panel_layout)
        
        # Botón para ocultar/mostrar panel
        self.toggle_panel_btn = QPushButton("◀")
        self.toggle_panel_btn.setFixedWidth(30)
        self.toggle_panel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6478FF, stop:1 #8296FF);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
                margin: 10px 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8296FF, stop:1 #A0B4FF);
            }
        """)
        self.toggle_panel_btn.clicked.connect(self.toggle_panel)
        
        # Visualizador 3D
        self.gl_widget = gl.GLViewWidget()
        self.gl_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0F0F1E, stop:1 #1A1A2E);
        """)
        self.gl_widget.setCameraPosition(distance=100, elevation=30, azimuth=45)
        
        # Grid moderno
        grid = gl.GLGridItem()
        grid.setSize(x=100, y=100, z=100)
        grid.setSpacing(x=5, y=5, z=5)
        grid.setColor((100, 120, 255, 100))
        self.gl_widget.addItem(grid)
        
        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.toggle_panel_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.gl_widget, stretch=1)
        central_widget.setLayout(self.main_layout)
        
        # Timer para rotación y animación
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(50)
        
    def toggle_panel(self):
        self.panel_visible = not self.panel_visible
        
        if self.panel_visible:
            self.control_panel.show()
            self.toggle_panel_btn.setText("◀")
        else:
            self.control_panel.hide()
            self.toggle_panel_btn.setText("▶")
            
    def toggle_rotation(self):
        self.rotation_active = self.rotation_toggle.toggle()
        
    def toggle_wave_animation(self):
        self.wave_animation_active = self.wave_toggle.toggle()
        
    def change_line_mode(self, index):
        self.line_mode = index
        self.update_visualization()
        
    def show_results_window(self):
        if self.image_data is None:
            return
        
        if self.results_window is None or not self.results_window.isVisible():
            self.results_window = ResultsWindow(self.image_data, self)
            self.results_window.show()
        else:
            self.results_window.activateWindow()
            self.results_window.raise_()
        
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", 
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_name:
            anim = QPropertyAnimation(self.load_btn, b"bg_color")
            anim.setDuration(300)
            anim.setStartValue(QColor(100, 120, 255))
            anim.setEndValue(QColor(50, 200, 150))
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.start()
            
            img = Image.open(file_name)
            self.image_data = np.array(img.convert('RGB'))
            
            h, w = self.image_data.shape[:2]
            self.info_label.setText(
                f"✓ Imagen cargada\n"
                f"Dimensiones: {w}x{h}px\n"
                f"Canales: RGB\n"
                f"Tamaño: {self.image_data.nbytes / 1024:.1f} KB"
            )
            
            self.fft_btn.setEnabled(True)
            self.results_btn.setEnabled(True)
            self.update_visualization()
            
    def update_visualization(self):
        if self.image_data is None:
            return
        
        # Limpiar items anteriores
        if self.wave_mesh:
            self.gl_widget.removeItem(self.wave_mesh)
        for line in self.wave_lines:
            self.gl_widget.removeItem(line)
        self.wave_lines.clear()
        
        amplitude = self.amplitude_slider.slider.value()
        resolution = self.resolution_slider.slider.value()
        
        h, w = self.image_data.shape[:2]
        step_x = max(1, w // resolution)
        step_y = max(1, h // resolution)
        
        x_coords = np.arange(0, w, step_x)
        y_coords = np.arange(0, h, step_y)
        
        # Crear malla de puntos
        points = []
        colors = []
        point_grid = {}
        brightness_grid = {}
        
        for i, yi in enumerate(y_coords):
            for j, xi in enumerate(x_coords):
                if yi < h and xi < w:
                    color = self.image_data[int(yi), int(xi)] / 255.0
                    brightness = np.mean(color)
                    brightness_grid[(i, j)] = brightness
                    
                    px = (xi - w/2) * 0.2
                    py = (yi - h/2) * 0.2
                    
                    point_grid[(i, j)] = (px, py, brightness)
        
        # Calcular animación de ondas con prioridad por brillo
        if self.wave_animation_active:
            direction = self.wave_direction_slider.slider.value()
            
            # Ordenar puntos por brillo (de mayor a menor)
            sorted_points = sorted(brightness_grid.items(), key=lambda x: x[1], reverse=True)
            
            for idx, ((i, j), brightness) in enumerate(sorted_points):
                px, py, _ = point_grid[(i, j)]
                
                # Fase de animación basada en orden de brillo
                phase_offset = idx * 0.1
                
                if direction == 0:  # Animación en X
                    wave_effect = np.sin(self.wave_offset + phase_offset) * brightness * amplitude * 0.5
                else:  # Animación en Y
                    wave_effect = np.sin(self.wave_offset + phase_offset) * brightness * amplitude * 0.5
                
                z = brightness * amplitude + wave_effect
                
                color = self.image_data[int(y_coords[i]), int(x_coords[j])] / 255.0
                points.append([px, py, z])
                colors.append((*color, 0.9))
                point_grid[(i, j)] = (px, py, z)
        else:
            # Sin animación, altura estática
            for (i, j), (px, py, brightness) in point_grid.items():
                z = brightness * amplitude
                color = self.image_data[int(y_coords[i]), int(x_coords[j])] / 255.0
                points.append([px, py, z])
                colors.append((*color, 0.9))
                point_grid[(i, j)] = (px, py, z)
        
        points = np.array(points)
        colors = np.array(colors)
        
        # Crear mesh de puntos 3D
        self.wave_mesh = gl.GLScatterPlotItem(
            pos=points,
            color=colors,
            size=4,
            pxMode=True
        )
        self.gl_widget.addItem(self.wave_mesh)
        
        # Crear líneas de conexión según el modo seleccionado
        if self.line_mode == 1 or self.line_mode == 3:  # Líneas X o X+Y
            for i in range(len(y_coords)):
                line_points = []
                for j in range(len(x_coords)):
                    if (i, j) in point_grid:
                        line_points.append(point_grid[(i, j)])
                
                if len(line_points) > 1:
                    line_points = np.array(line_points)
                    line = gl.GLLinePlotItem(
                        pos=line_points,
                        color=(0.4, 0.6, 1.0, 0.7),
                        width=2,
                        antialias=True
                    )
                    self.gl_widget.addItem(line)
                    self.wave_lines.append(line)
        
        if self.line_mode == 2 or self.line_mode == 3:  # Líneas Y o X+Y
            for j in range(len(x_coords)):
                line_points = []
                for i in range(len(y_coords)):
                    if (i, j) in point_grid:
                        line_points.append(point_grid[(i, j)])
                
                if len(line_points) > 1:
                    line_points = np.array(line_points)
                    line = gl.GLLinePlotItem(
                        pos=line_points,
                        color=(1.0, 0.5, 0.3, 0.7),
                        width=2,
                        antialias=True
                    )
                    self.gl_widget.addItem(line)
                    self.wave_lines.append(line)
        
    def show_fft_analysis(self):
        if self.image_data is None:
            return
        
        gray = np.mean(self.image_data, axis=2)
        
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shift)
        
        magnitude_log = np.log(magnitude + 1)
        magnitude_norm = (magnitude_log - magnitude_log.min()) / (magnitude_log.max() - magnitude_log.min())
        
        h, w = magnitude.shape
        resolution = self.resolution_slider.slider.value()
        step_x = max(1, w // resolution)
        step_y = max(1, h // resolution)
        
        x = np.arange(0, w, step_x)
        y = np.arange(0, h, step_y)
        
        points = []
        colors = []
        
        for yi in y:
            for xi in x:
                if yi < h and xi < w:
                    mag_value = magnitude_norm[int(yi), int(xi)]
                    
                    px = (xi - w/2) * 0.2
                    py = (yi - h/2) * 0.2
                    pz = mag_value * 50
                    
                    points.append([px, py, pz])
                    
                    color_r = mag_value
                    color_g = 0.3
                    color_b = 1.0 - mag_value
                    colors.append((color_r, color_g, color_b, 0.9))
        
        if self.wave_mesh:
            self.gl_widget.removeItem(self.wave_mesh)
        for line in self.wave_lines:
            self.gl_widget.removeItem(line)
        self.wave_lines.clear()
        
        points = np.array(points)
        colors = np.array(colors)
        
        self.wave_mesh = gl.GLScatterPlotItem(
            pos=points,
            color=colors,
            size=4,
            pxMode=True
        )
        
        self.gl_widget.addItem(self.wave_mesh)
        
    def animate(self):
        # Rotación automática
        if self.rotation_active and self.image_data is not None:
            speed = self.rotation_speed_slider.slider.value()
            self.rotation_angle += speed * 0.5
            self.gl_widget.setCameraPosition(
                distance=100, 
                elevation=30, 
                azimuth=self.rotation_angle
            )
        
        # Animación de ondas
        if self.wave_animation_active and self.image_data is not None:
            wave_speed = self.wave_speed_slider.slider.value()
            self.wave_offset += wave_speed * 0.05
            self.update_visualization()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = WaveVisualizer()
    window.show()
    sys.exit(app.exec())