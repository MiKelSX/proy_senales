import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QSlider, 
                             QHBoxLayout, QFrame, QGraphicsDropShadowEffect, 
                             QScrollArea, QGridLayout, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint
from PyQt6.QtGui import QFont, QColor, QPalette, QCursor
import pyqtgraph.opengl as gl
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from PIL import Image
from scipy.signal import find_peaks
from scipy.interpolate import interp1d

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
        self.setWindowTitle("📊 Dashboard de Análisis")
        self.setGeometry(150, 100, 1300, 800)
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(12, 12, 20))
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
                background: #1A1A2A;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #6478FF;
                border-radius: 4px;
                min-height: 20px;
            }
        """)
        
        content = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título compacto
        title = QLabel("⚡ DASHBOARD ANÁLISIS FFT")
        title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 22px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
                padding: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6478FF, stop:1 #8296FF);
                border-radius: 12px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title)
        
        content.setLayout(self.main_layout)
        scroll.setWidget(content)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        central.setLayout(layout)
        
    def create_metric_card(self, symbol, value, label):
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1A1A2A, stop:1 #252535);
                border-radius: 12px;
                border: 1px solid #3A3A5A;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(12, 8, 12, 8)
        
        symbol_label = QLabel(symbol)
        symbol_label.setStyleSheet("""
            QLabel {
                color: #6478FF;
                font-size: 20px;
                font-weight: 700;
                font-family: 'Cambria Math', serif;
            }
        """)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 600;
                font-family: 'Consolas', monospace;
            }
        """)
        value_label.setWordWrap(True)
        
        label_text = QLabel(label)
        label_text.setStyleSheet("""
            QLabel {
                color: #8090B0;
                font-size: 10px;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        layout.addWidget(symbol_label)
        layout.addWidget(value_label)
        layout.addWidget(label_text)
        layout.addStretch()
        
        card.setLayout(layout)
        return card
        
    def create_chart_card(self, title, plot_widget):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1A1A2A, stop:1 #252535);
                border-radius: 12px;
                border: 1px solid #3A3A5A;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(plot_widget)
        
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
        std_mag = np.std(magnitude)
        total_energy = np.sum(power_spectrum)
        
        # Entropía espectral
        normalized_power = power_spectrum / np.sum(power_spectrum)
        spectral_entropy = -np.sum(normalized_power * np.log2(normalized_power + 1e-12))
        
        # SNR
        signal_power = np.max(power_spectrum)
        noise_power = np.median(power_spectrum)
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 0
        
        # Crear grid de métricas
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(10)
        
        metrics_grid.addWidget(self.create_metric_card("ℱ", f"{h}×{w}", "Dimensiones FFT"), 0, 0)
        metrics_grid.addWidget(self.create_metric_card("μ(|F|)", f"{mean_mag:.3e}", "Magnitud promedio"), 0, 1)
        metrics_grid.addWidget(self.create_metric_card("max", f"{max_mag:.3e}", "Magnitud máxima"), 0, 2)
        metrics_grid.addWidget(self.create_metric_card("σ", f"{std_mag:.3e}", "Desviación estándar"), 0, 3)
        
        metrics_grid.addWidget(self.create_metric_card("E", f"{total_energy:.3e}", "Energía total"), 1, 0)
        metrics_grid.addWidget(self.create_metric_card("H", f"{spectral_entropy:.2f}", "Entropía espectral"), 1, 1)
        metrics_grid.addWidget(self.create_metric_card("SNR", f"{snr:.1f} dB", "Señal/Ruido"), 1, 2)
        metrics_grid.addWidget(self.create_metric_card("⟨φ⟩", f"{np.mean(phase):.3f}", "Fase promedio"), 1, 3)
        
        metrics_container = QWidget()
        metrics_container.setLayout(metrics_grid)
        self.main_layout.addWidget(metrics_container)
        
        # Gráficos
        charts_grid = QGridLayout()
        charts_grid.setSpacing(10)
        
        # Gráfico 1: Espectro de magnitud
        mag_plot = PlotWidget()
        mag_plot.setBackground('#1A1A2A')
        mag_plot.setFixedHeight(200)
        mag_slice = magnitude[h//2, :]
        mag_plot.plot(mag_slice, pen=pg.mkPen(color='#6478FF', width=2))
        mag_plot.setLabel('left', 'Magnitud')
        mag_plot.setLabel('bottom', 'Frecuencia')
        mag_plot.showGrid(x=True, y=True, alpha=0.2)
        
        # Gráfico 2: Distribución de fase
        phase_plot = PlotWidget()
        phase_plot.setBackground('#1A1A2A')
        phase_plot.setFixedHeight(200)
        phase_hist, phase_bins = np.histogram(phase.flatten(), bins=50)
        phase_plot.plot(phase_bins[:-1], phase_hist, pen=pg.mkPen(color='#FF6B9D', width=2), fillLevel=0, brush=(255, 107, 157, 100))
        phase_plot.setLabel('left', 'Frecuencia')
        phase_plot.setLabel('bottom', 'Fase (rad)')
        phase_plot.showGrid(x=True, y=True, alpha=0.2)
        
        # Gráfico 3: Espectro de potencia logarítmico
        power_plot = PlotWidget()
        power_plot.setBackground('#1A1A2A')
        power_plot.setFixedHeight(200)
        power_log = np.log10(power_spectrum[h//2, :] + 1)
        power_plot.plot(power_log, pen=pg.mkPen(color='#50C878', width=2))
        power_plot.setLabel('left', 'log₁₀(Potencia)')
        power_plot.setLabel('bottom', 'Frecuencia')
        power_plot.showGrid(x=True, y=True, alpha=0.2)
        
        # Gráfico 4: Mapa de calor 2D de magnitud
        magnitude_log = np.log(magnitude + 1)
        img_item = pg.ImageItem(magnitude_log)
        img_item.setLookupTable(pg.colormap.get('viridis').getLookupTable())
        
        heat_plot = PlotWidget()
        heat_plot.setBackground('#1A1A2A')
        heat_plot.setFixedHeight(200)
        heat_plot.addItem(img_item)
        heat_plot.setAspectLocked(False)
        heat_plot.setLabel('left', 'Y')
        heat_plot.setLabel('bottom', 'X')
        
        charts_grid.addWidget(self.create_chart_card("📈 Espectro de Magnitud (Corte central)", mag_plot), 0, 0)
        charts_grid.addWidget(self.create_chart_card("📊 Distribución de Fase", phase_plot), 0, 1)
        charts_grid.addWidget(self.create_chart_card("⚡ Espectro de Potencia (log)", power_plot), 1, 0)
        charts_grid.addWidget(self.create_chart_card("🔥 Mapa de Magnitud 2D", heat_plot), 1, 1)
        
        charts_container = QWidget()
        charts_container.setLayout(charts_grid)
        self.main_layout.addWidget(charts_container)
        
        # Sección FFT 2D - Proyecciones
        fft_section = QLabel("🔬 TRANSFORMADA DE FOURIER 2D - PROYECCIONES")
        fft_section.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
                padding: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6478FF, stop:1 #8296FF);
                border-radius: 12px;
                margin-top: 10px;
            }
        """)
        self.main_layout.addWidget(fft_section)
        
        fft_grid = QGridLayout()
        fft_grid.setSpacing(10)
        
        # Crear colormaps personalizados compatibles
        def create_colormap(name):
            if name == 'viridis':
                colors = np.array([
                    [68, 1, 84], [72, 40, 120], [62, 73, 137], [49, 104, 142],
                    [38, 130, 142], [31, 158, 137], [53, 183, 121], [109, 205, 89],
                    [180, 222, 44], [253, 231, 37]
                ])
            elif name == 'plasma':
                colors = np.array([
                    [13, 8, 135], [75, 3, 161], [125, 3, 168], [168, 34, 150],
                    [203, 70, 121], [229, 107, 93], [248, 148, 65], [253, 195, 40],
                    [246, 243, 75], [240, 249, 33]
                ])
            elif name == 'inferno':
                colors = np.array([
                    [0, 0, 4], [40, 11, 84], [101, 21, 110], [159, 42, 99],
                    [212, 72, 66], [245, 125, 21], [250, 193, 39], [245, 251, 134],
                    [252, 255, 164], [252, 255, 164]
                ])
            elif name == 'hot':
                colors = np.array([
                    [0, 0, 0], [128, 0, 0], [255, 0, 0], [255, 128, 0],
                    [255, 255, 0], [255, 255, 128], [255, 255, 255], [255, 255, 255],
                    [255, 255, 255], [255, 255, 255]
                ])
            elif name == 'turbo':
                colors = np.array([
                    [48, 18, 59], [62, 73, 137], [33, 145, 140], [53, 183, 121],
                    [109, 205, 89], [180, 222, 44], [251, 206, 34], [248, 148, 65],
                    [238, 63, 51], [122, 4, 3]
                ])
            else:
                colors = np.array([[0, 0, 255], [255, 0, 0]])
            
            # Interpolar para 256 niveles
            from scipy.interpolate import interp1d
            x = np.linspace(0, 1, len(colors))
            x_new = np.linspace(0, 1, 256)
            r_interp = interp1d(x, colors[:, 0], kind='cubic')
            g_interp = interp1d(x, colors[:, 1], kind='cubic')
            b_interp = interp1d(x, colors[:, 2], kind='cubic')
            
            lut = np.zeros((256, 3), dtype=np.ubyte)
            lut[:, 0] = np.clip(r_interp(x_new), 0, 255).astype(np.ubyte)
            lut[:, 1] = np.clip(g_interp(x_new), 0, 255).astype(np.ubyte)
            lut[:, 2] = np.clip(b_interp(x_new), 0, 255).astype(np.ubyte)
            
            return lut
        
        # FFT 2D - Vista XY (Magnitud)
        fft_xy_mag = pg.ImageItem(magnitude_log)
        fft_xy_mag.setLookupTable(create_colormap('viridis'))
        fft_xy_plot = PlotWidget()
        fft_xy_plot.setBackground('#1A1A2A')
        fft_xy_plot.setFixedHeight(200)
        fft_xy_plot.addItem(fft_xy_mag)
        fft_xy_plot.setAspectLocked(True)
        fft_xy_plot.setLabel('left', 'Y')
        fft_xy_plot.setLabel('bottom', 'X')
        
        # FFT 2D - Vista XZ (Proyección lateral)
        fft_xz = np.sum(magnitude_log, axis=0)
        fft_xz_norm = (fft_xz - fft_xz.min()) / (fft_xz.max() - fft_xz.min() + 1e-10)
        fft_xz_2d = np.tile(fft_xz_norm, (50, 1))
        fft_xz_img = pg.ImageItem(fft_xz_2d)
        fft_xz_img.setLookupTable(create_colormap('plasma'))
        fft_xz_plot = PlotWidget()
        fft_xz_plot.setBackground('#1A1A2A')
        fft_xz_plot.setFixedHeight(200)
        fft_xz_plot.addItem(fft_xz_img)
        fft_xz_plot.setLabel('left', 'Z (Magnitud)')
        fft_xz_plot.setLabel('bottom', 'X')
        
        # FFT 2D - Vista YZ (Proyección frontal)
        fft_yz = np.sum(magnitude_log, axis=1)
        fft_yz_norm = (fft_yz - fft_yz.min()) / (fft_yz.max() - fft_yz.min() + 1e-10)
        fft_yz_2d = np.tile(fft_yz_norm.reshape(-1, 1), (1, 50))
        fft_yz_img = pg.ImageItem(fft_yz_2d)
        fft_yz_img.setLookupTable(create_colormap('inferno'))
        fft_yz_plot = PlotWidget()
        fft_yz_plot.setBackground('#1A1A2A')
        fft_yz_plot.setFixedHeight(200)
        fft_yz_plot.addItem(fft_yz_img)
        fft_yz_plot.setLabel('left', 'Y')
        fft_yz_plot.setLabel('bottom', 'Z (Magnitud)')
        
        fft_grid.addWidget(self.create_chart_card("📐 FFT 2D - Plano XY (Magnitud)", fft_xy_plot), 0, 0)
        fft_grid.addWidget(self.create_chart_card("📏 FFT 2D - Plano XZ (Proyección)", fft_xz_plot), 0, 1)
        fft_grid.addWidget(self.create_chart_card("📊 FFT 2D - Plano YZ (Proyección)", fft_yz_plot), 0, 2)
        
        fft_container = QWidget()
        fft_container.setLayout(fft_grid)
        self.main_layout.addWidget(fft_container)
        
        # Sección análisis Fourier avanzado
        fourier_section = QLabel("🌊 ANÁLISIS DE FOURIER COMPLETO")
        fourier_section.setStyleSheet(fft_section.styleSheet())
        self.main_layout.addWidget(fourier_section)
        
        fourier_grid = QGridLayout()
        fourier_grid.setSpacing(10)
        
        # Componentes real e imaginaria
        real_part = np.real(fft_shift)
        imag_part = np.imag(fft_shift)
        
        real_plot = PlotWidget()
        real_plot.setBackground('#1A1A2A')
        real_plot.setFixedHeight(200)
        real_slice = real_part[h//2, :]
        real_plot.plot(real_slice, pen=pg.mkPen(color='#50C878', width=2))
        real_plot.setLabel('left', 'Re(F)')
        real_plot.setLabel('bottom', 'Frecuencia')
        real_plot.showGrid(x=True, y=True, alpha=0.2)
        
        imag_plot = PlotWidget()
        imag_plot.setBackground('#1A1A2A')
        imag_plot.setFixedHeight(200)
        imag_slice = imag_part[h//2, :]
        imag_plot.plot(imag_slice, pen=pg.mkPen(color='#FF6B9D', width=2))
        imag_plot.setLabel('left', 'Im(F)')
        imag_plot.setLabel('bottom', 'Frecuencia')
        imag_plot.showGrid(x=True, y=True, alpha=0.2)
        
        # Densidad espectral de potencia 2D
        psd_2d = power_spectrum / np.sum(power_spectrum)
        psd_log = np.log10(psd_2d + 1e-12)
        psd_img = pg.ImageItem(psd_log)
        psd_img.setLookupTable(create_colormap('hot'))
        psd_plot = PlotWidget()
        psd_plot.setBackground('#1A1A2A')
        psd_plot.setFixedHeight(200)
        psd_plot.addItem(psd_img)
        psd_plot.setLabel('left', 'Y')
        psd_plot.setLabel('bottom', 'X')
        
        fourier_grid.addWidget(self.create_chart_card("📈 Componente Real Re(F)", real_plot), 0, 0)
        fourier_grid.addWidget(self.create_chart_card("📉 Componente Imaginaria Im(F)", imag_plot), 0, 1)
        fourier_grid.addWidget(self.create_chart_card("🔥 Densidad Espectral de Potencia 2D", psd_plot), 0, 2)
        
        # Frecuencias radiales y angulares
        center_y, center_x = h // 2, w // 2
        y_coords, x_coords = np.ogrid[:h, :w]
        r = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
        theta = np.arctan2(y_coords - center_y, x_coords - center_x)
        
        # Perfil radial
        max_r = int(min(center_x, center_y))
        radial_profile = np.zeros(max_r)
        for i in range(max_r):
            mask = (r >= i) & (r < i + 1)
            if np.sum(mask) > 0:
                radial_profile[i] = np.mean(magnitude[mask])
        
        radial_plot = PlotWidget()
        radial_plot.setBackground('#1A1A2A')
        radial_plot.setFixedHeight(200)
        radial_plot.plot(radial_profile, pen=pg.mkPen(color='#FFD700', width=2))
        radial_plot.setLabel('left', 'Magnitud')
        radial_plot.setLabel('bottom', 'Frecuencia Radial')
        radial_plot.showGrid(x=True, y=True, alpha=0.2)
        
        # Perfil angular
        n_angles = 360
        angular_profile = np.zeros(n_angles)
        for i in range(n_angles):
            angle_min = np.deg2rad(i - 1)
            angle_max = np.deg2rad(i + 1)
            mask = (theta >= angle_min) & (theta < angle_max)
            if np.sum(mask) > 0:
                angular_profile[i] = np.mean(magnitude[mask])
        
        angular_plot = PlotWidget()
        angular_plot.setBackground('#1A1A2A')
        angular_plot.setFixedHeight(200)
        angles = np.arange(n_angles)
        angular_plot.plot(angles, angular_profile, pen=pg.mkPen(color='#00CED1', width=2))
        angular_plot.setLabel('left', 'Magnitud')
        angular_plot.setLabel('bottom', 'Ángulo (grados)')
        angular_plot.showGrid(x=True, y=True, alpha=0.2)
        
        fourier_grid.addWidget(self.create_chart_card("🎯 Perfil Radial de Frecuencias", radial_plot), 1, 0)
        fourier_grid.addWidget(self.create_chart_card("🔄 Perfil Angular de Frecuencias", angular_plot), 1, 1)
        
        # Barra de frecuencias dominantes
        flat_mag = magnitude.flatten()
        top_indices = np.argpartition(flat_mag, -10)[-10:]
        top_freqs = sorted(flat_mag[top_indices], reverse=True)
        
        freq_bar = PlotWidget()
        freq_bar.setBackground('#1A1A2A')
        freq_bar.setFixedHeight(200)
        x_bar = np.arange(len(top_freqs))
        bargraph = pg.BarGraphItem(x=x_bar, height=top_freqs, width=0.6, brush='#8296FF')
        freq_bar.addItem(bargraph)
        freq_bar.setLabel('left', 'Magnitud')
        freq_bar.setLabel('bottom', 'Top Frecuencias')
        freq_bar.showGrid(y=True, alpha=0.2)
        
        fourier_grid.addWidget(self.create_chart_card("🎯 Top 10 Frecuencias Dominantes", freq_bar), 1, 2)
        
        fourier_container = QWidget()
        fourier_container.setLayout(fourier_grid)
        self.main_layout.addWidget(fourier_container)
        
        # Sección Transformada de Laplace (aproximación discreta)
        laplace_section = QLabel("⚡ TRANSFORMADA DE LAPLACE (Aproximación Discreta)")
        laplace_section.setStyleSheet(fft_section.styleSheet())
        self.main_layout.addWidget(laplace_section)
        
        laplace_grid = QGridLayout()
        laplace_grid.setSpacing(10)
        
        # Aproximación de Laplace usando decaimiento exponencial
        # L{f(t)} ≈ Σ f(n)e^(-sn) donde s = σ + jω
        t = np.linspace(0, 10, gray.shape[1])
        signal_1d = gray[h//2, :]
        
        # Respuesta en frecuencia para diferentes valores de sigma
        sigmas = np.linspace(0.01, 2, 100)
        omega = np.linspace(-np.pi, np.pi, 100)
        
        laplace_mag = np.zeros((len(sigmas), len(omega)))
        for i, sigma in enumerate(sigmas):
            for j, w in enumerate(omega):
                s = sigma + 1j * w
                dt = t[1] - t[0] if len(t) > 1 else 1
                laplace_val = np.sum(signal_1d * np.exp(-s * t[:len(signal_1d)])) * dt
                laplace_mag[i, j] = np.abs(laplace_val)
        
        laplace_img = pg.ImageItem(np.log10(laplace_mag + 1))
        laplace_img.setLookupTable(create_colormap('turbo'))
        laplace_plot = PlotWidget()
        laplace_plot.setBackground('#1A1A2A')
        laplace_plot.setFixedHeight(200)
        laplace_plot.addItem(laplace_img)
        laplace_plot.setLabel('left', 'σ (parte real)')
        laplace_plot.setLabel('bottom', 'ω (parte imaginaria)')
        
        # Respuesta al impulso (inversa aproximada)
        impulse_response = np.fft.ifft(magnitude[h//2, :]).real
        impulse_plot = PlotWidget()
        impulse_plot.setBackground('#1A1A2A')
        impulse_plot.setFixedHeight(200)
        impulse_plot.plot(impulse_response[:200], pen=pg.mkPen(color='#FF69B4', width=2))
        impulse_plot.setLabel('left', 'Amplitud')
        impulse_plot.setLabel('bottom', 'Tiempo')
        impulse_plot.showGrid(x=True, y=True, alpha=0.2)
        
        # Diagrama de polos y ceros (aproximado)
        zeros_poles_plot = PlotWidget()
        zeros_poles_plot.setBackground('#1A1A2A')
        zeros_poles_plot.setFixedHeight(200)
        
        # Encontrar máximos locales como "polos"
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(np.abs(signal_1d), height=np.mean(signal_1d))
        
        # Círculo unitario
        theta_circle = np.linspace(0, 2*np.pi, 100)
        x_circle = np.cos(theta_circle)
        y_circle = np.sin(theta_circle)
        zeros_poles_plot.plot(x_circle, y_circle, pen=pg.mkPen(color='#FFFFFF', width=1, style=Qt.PenStyle.DashLine))
        
        # Polos (x) y ceros (o)
        if len(peaks) > 0:
            pole_angles = 2 * np.pi * peaks / len(signal_1d)
            pole_x = 0.8 * np.cos(pole_angles)
            pole_y = 0.8 * np.sin(pole_angles)
            zeros_poles_plot.plot(pole_x, pole_y, pen=None, symbol='x', symbolSize=12, symbolBrush='#FF6B6B')
        
        zeros_poles_plot.setLabel('left', 'Imaginario')
        zeros_poles_plot.setLabel('bottom', 'Real')
        zeros_poles_plot.showGrid(x=True, y=True, alpha=0.2)
        zeros_poles_plot.setAspectLocked(True)
        
        laplace_grid.addWidget(self.create_chart_card("🌐 Transformada de Laplace |L{f}(s)|", laplace_plot), 0, 0)
        laplace_grid.addWidget(self.create_chart_card("⚡ Respuesta al Impulso h(t)", impulse_plot), 0, 1)
        laplace_grid.addWidget(self.create_chart_card("⭕ Diagrama Polos-Ceros (Plano S)", zeros_poles_plot), 0, 2)
        
        laplace_container = QWidget()
        laplace_container.setLayout(laplace_grid)
        self.main_layout.addWidget(laplace_container)

class TooltipLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLabel {
                background: rgba(30, 30, 46, 240);
                color: #FFFFFF;
                border: 2px solid #6478FF;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 11px;
                font-family: 'Consolas', monospace;
            }
        """)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.hide()

class WaveVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_data = None
        self.wave_mesh = None
        self.wave_lines = []
        self.point_data = []
        self.rotation_angle = 0
        self.wave_offset = 0
        self.panel_visible = True
        self.rotation_active = True
        self.wave_animation_active = False
        self.line_mode = 0
        self.tooltip_enabled = False
        self.results_window = None
        self.tooltip = TooltipLabel()
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
        """)
        
        scroll_content = QWidget()
        control_layout = QVBoxLayout()
        control_layout.setSpacing(20)
        control_layout.setContentsMargins(20, 20, 20, 20)
        
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
        
        self.load_btn = AnimatedButton("📁 Cargar Imagen")
        self.load_btn.clicked.connect(self.load_image)
        
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
        
        # Toggle tooltip
        self.tooltip_toggle = ToggleButton("Activar Info", "Desactivar Info", "🔍", "🔍")
        self.tooltip_toggle.clicked.connect(self.toggle_tooltip)
        
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
            }
            QComboBox QAbstractItemView {
                background: #2A2A3E;
                color: #E0E0E0;
                selection-background-color: #6478FF;
                border: 2px solid #6478FF;
            }
        """)
        self.line_mode_combo.currentIndexChanged.connect(self.change_line_mode)
        
        lines_layout.addWidget(lines_title)
        lines_layout.addWidget(self.line_mode_combo)
        lines_container.setLayout(lines_layout)
        
        rot_label = QLabel("🔄 ROTACIÓN")
        rot_label.setStyleSheet(viz_label.styleSheet())
        
        self.rotation_toggle = ToggleButton("Pausar", "Reanudar", "⏸", "▶")
        self.rotation_toggle.is_active = True
        self.rotation_toggle.update_state()
        self.rotation_toggle.clicked.connect(self.toggle_rotation)
        
        self.rotation_speed_slider = ModernSlider("Velocidad", 0, 20, 2)
        
        wave_label = QLabel("〰️ ANIMACIÓN")
        wave_label.setStyleSheet(viz_label.styleSheet())
        
        self.wave_toggle = ToggleButton("Activar", "Desactivar", "▶", "⏸")
        self.wave_toggle.clicked.connect(self.toggle_wave_animation)
        
        self.wave_speed_slider = ModernSlider("Velocidad", 1, 20, 5)
        self.wave_direction_slider = ModernSlider("Dirección", 0, 1, 0)
        
        self.results_btn = AnimatedButton("🧮 Dashboard")
        self.results_btn.clicked.connect(self.show_results_window)
        self.results_btn.setEnabled(False)
        
        self.fft_btn = AnimatedButton("⚡ FFT View")
        self.fft_btn.clicked.connect(self.show_fft_analysis)
        self.fft_btn.setEnabled(False)
        
        control_layout.addWidget(title)
        control_layout.addWidget(self.load_btn)
        control_layout.addWidget(self.info_label)
        control_layout.addWidget(viz_label)
        control_layout.addWidget(self.amplitude_slider)
        control_layout.addWidget(self.resolution_slider)
        control_layout.addWidget(self.tooltip_toggle)
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
        
        self.gl_widget = gl.GLViewWidget()
        self.gl_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0F0F1E, stop:1 #1A1A2E);
        """)
        self.gl_widget.setCameraPosition(distance=100, elevation=30, azimuth=45)
        self.gl_widget.setMouseTracking(True)
        
        self.grid_item = gl.GLGridItem()
        self.gl_widget.addItem(self.grid_item)
        
        self.main_layout.addWidget(self.control_panel)
        self.main_layout.addWidget(self.toggle_panel_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        self.main_layout.addWidget(self.gl_widget, stretch=1)
        central_widget.setLayout(self.main_layout)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(50)
        
        self.tooltip_timer = QTimer()
        self.tooltip_timer.timeout.connect(self.check_hover)
        self.tooltip_timer.start(100)
        
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
        
    def toggle_tooltip(self):
        self.tooltip_enabled = self.tooltip_toggle.toggle()
        if not self.tooltip_enabled:
            self.tooltip.hide()
        
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
            
            # Ajustar grid al tamaño de la imagen
            self.gl_widget.removeItem(self.grid_item)
            grid_size_x = max(50, w * 0.02)
            grid_size_y = max(50, h * 0.02)
            self.grid_item = gl.GLGridItem()
            self.grid_item.setSize(x=grid_size_x, y=grid_size_y, z=50)
            self.grid_item.setSpacing(x=grid_size_x/20, y=grid_size_y/20, z=5)
            self.grid_item.setColor((100, 120, 255, 100))
            self.gl_widget.addItem(self.grid_item)
            
            self.fft_btn.setEnabled(True)
            self.results_btn.setEnabled(True)
            self.update_visualization()
            
    def update_visualization(self):
        if self.image_data is None:
            return
        
        if self.wave_mesh:
            self.gl_widget.removeItem(self.wave_mesh)
        for line in self.wave_lines:
            self.gl_widget.removeItem(line)
        self.wave_lines.clear()
        self.point_data.clear()
        
        amplitude = self.amplitude_slider.slider.value()
        resolution = self.resolution_slider.slider.value()
        
        h, w = self.image_data.shape[:2]
        step_x = max(1, w // resolution)
        step_y = max(1, h // resolution)
        
        x_coords = np.arange(0, w, step_x)
        y_coords = np.arange(0, h, step_y)
        
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
                    point_grid[(i, j)] = (px, py, brightness, color, int(xi), int(yi))
        
        if self.wave_animation_active:
            direction = self.wave_direction_slider.slider.value()
            sorted_points = sorted(brightness_grid.items(), key=lambda x: x[1], reverse=True)
            
            for idx, ((i, j), brightness) in enumerate(sorted_points):
                px, py, _, color, xi, yi = point_grid[(i, j)]
                phase_offset = idx * 0.1
                
                if direction == 0:
                    wave_effect = np.sin(self.wave_offset + phase_offset) * brightness * amplitude * 0.5
                else:
                    wave_effect = np.sin(self.wave_offset + phase_offset) * brightness * amplitude * 0.5
                
                z = brightness * amplitude + wave_effect
                points.append([px, py, z])
                colors.append((*color, 0.9))
                point_grid[(i, j)] = (px, py, z, color, xi, yi)
                self.point_data.append({
                    'pos': [px, py, z],
                    'color': color,
                    'brightness': brightness,
                    'coords': (xi, yi),
                    'amplitude': z
                })
        else:
            for (i, j), (px, py, brightness, color, xi, yi) in point_grid.items():
                z = brightness * amplitude
                points.append([px, py, z])
                colors.append((*color, 0.9))
                point_grid[(i, j)] = (px, py, z, color, xi, yi)
                self.point_data.append({
                    'pos': [px, py, z],
                    'color': color,
                    'brightness': brightness,
                    'coords': (xi, yi),
                    'amplitude': z
                })
        
        points = np.array(points)
        colors = np.array(colors)
        
        self.wave_mesh = gl.GLScatterPlotItem(
            pos=points,
            color=colors,
            size=4,
            pxMode=True
        )
        self.gl_widget.addItem(self.wave_mesh)
        
        if self.line_mode == 1 or self.line_mode == 3:
            for i in range(len(y_coords)):
                line_points = []
                for j in range(len(x_coords)):
                    if (i, j) in point_grid:
                        px, py, z, _, _, _ = point_grid[(i, j)]
                        line_points.append([px, py, z])
                
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
        
        if self.line_mode == 2 or self.line_mode == 3:
            for j in range(len(x_coords)):
                line_points = []
                for i in range(len(y_coords)):
                    if (i, j) in point_grid:
                        px, py, z, _, _, _ = point_grid[(i, j)]
                        line_points.append([px, py, z])
                
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
    
    def check_hover(self):
        if not self.tooltip_enabled or not self.point_data:
            return
        
        cursor_pos = self.gl_widget.mapFromGlobal(QCursor.pos())
        if not self.gl_widget.rect().contains(cursor_pos):
            self.tooltip.hide()
            return
        
        # Buscar punto más cercano al cursor (simplificado)
        closest_point = None
        min_dist = float('inf')
        
        for point in self.point_data:
            px, py, pz = point['pos']
            # Proyección simple 2D
            screen_dist = ((cursor_pos.x() - self.gl_widget.width()/2) ** 2 + 
                          (cursor_pos.y() - self.gl_widget.height()/2) ** 2) ** 0.5
            
            if screen_dist < min_dist and screen_dist < 100:
                min_dist = screen_dist
                closest_point = point
        
        if closest_point:
            r, g, b = closest_point['color']
            text = (f"📍 Pos: ({closest_point['coords'][0]}, {closest_point['coords'][1]})\n"
                   f"🎨 RGB: ({int(r*255)}, {int(g*255)}, {int(b*255)})\n"
                   f"📊 Brillo: {closest_point['brightness']:.3f}\n"
                   f"⚡ Amplitud: {closest_point['amplitude']:.2f}")
            
            self.tooltip.setText(text)
            self.tooltip.adjustSize()
            
            global_pos = self.gl_widget.mapToGlobal(cursor_pos)
            self.tooltip.move(global_pos.x() + 15, global_pos.y() + 15)
            self.tooltip.show()
        else:
            self.tooltip.hide()
        
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
        if self.rotation_active and self.image_data is not None:
            speed = self.rotation_speed_slider.slider.value()
            self.rotation_angle += speed * 0.5
            self.gl_widget.setCameraPosition(
                distance=100, 
                elevation=30, 
                azimuth=self.rotation_angle
            )
        
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