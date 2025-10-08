import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QSlider, 
                             QHBoxLayout, QFrame, QGraphicsDropShadowEffect)
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

class ModernSlider(QWidget):
    def __init__(self, label_text, min_val, max_val, default_val, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        self.label = QLabel(label_text)
        self.label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        self.value_label = QLabel(str(default_val))
        self.value_label.setStyleSheet("""
            QLabel {
                color: #6478FF;
                font-size: 16px;
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
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6478FF, stop:1 #8296FF);
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
                border: 2px solid #FFFFFF;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8296FF, stop:1 #A0B4FF);
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6478FF, stop:1 #8296FF);
                border-radius: 4px;
            }
        """)
        
        self.slider.valueChanged.connect(lambda v: self.value_label.setText(str(v)))
        
        layout.addLayout(header)
        layout.addWidget(self.slider)
        self.setLayout(layout)

class WaveVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_data = None
        self.wave_mesh = None
        self.rotation_angle = 0
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Wave Visualizer 3D - FFT Analysis")
        self.setGeometry(100, 100, 1400, 900)
        
        # Tema oscuro moderno
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        self.setPalette(palette)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Panel de control lateral
        control_panel = QFrame()
        control_panel.setMaximumWidth(350)
        control_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E1E2E, stop:1 #2A2A3E);
                border-radius: 25px;
                padding: 20px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 10)
        control_panel.setGraphicsEffect(shadow)
        
        control_layout = QVBoxLayout()
        control_layout.setSpacing(25)
        
        # Título
        title = QLabel("🌊 Wave Visualizer")
        title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 28px;
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
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                background: #2A2A3E;
                padding: 15px;
                border-radius: 15px;
            }
        """)
        self.info_label.setWordWrap(True)
        
        # Controles deslizantes
        self.amplitude_slider = ModernSlider("Amplitud de Onda", 1, 100, 20)
        self.resolution_slider = ModernSlider("Resolución", 10, 200, 50)
        self.rotation_speed_slider = ModernSlider("Vel. Rotación", 0, 10, 2)
        
        self.amplitude_slider.slider.valueChanged.connect(self.update_visualization)
        self.resolution_slider.slider.valueChanged.connect(self.update_visualization)
        
        # Botón de análisis FFT
        self.fft_btn = AnimatedButton("⚡ Análisis FFT")
        self.fft_btn.clicked.connect(self.show_fft_analysis)
        self.fft_btn.setEnabled(False)
        
        # Info FFT
        self.fft_info = QLabel("")
        self.fft_info.setStyleSheet("""
            QLabel {
                color: #6478FF;
                font-size: 12px;
                font-family: 'Consolas', monospace;
                background: #1E1E2E;
                padding: 15px;
                border-radius: 15px;
                border: 2px solid #6478FF;
            }
        """)
        self.fft_info.setWordWrap(True)
        
        control_layout.addWidget(title)
        control_layout.addWidget(self.load_btn)
        control_layout.addWidget(self.info_label)
        control_layout.addWidget(self.amplitude_slider)
        control_layout.addWidget(self.resolution_slider)
        control_layout.addWidget(self.rotation_speed_slider)
        control_layout.addWidget(self.fft_btn)
        control_layout.addWidget(self.fft_info)
        control_layout.addStretch()
        
        control_panel.setLayout(control_layout)
        
        # Visualizador 3D
        self.gl_widget = gl.GLViewWidget()
        self.gl_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0F0F1E, stop:1 #1A1A2E);
            border-radius: 25px;
        """)
        self.gl_widget.setCameraPosition(distance=100, elevation=30, azimuth=45)
        
        # Grid moderno
        grid = gl.GLGridItem()
        grid.setSize(x=100, y=100, z=100)
        grid.setSpacing(x=5, y=5, z=5)
        grid.setColor((100, 120, 255, 100))
        self.gl_widget.addItem(grid)
        
        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.gl_widget, stretch=1)
        central_widget.setLayout(main_layout)
        
        # Timer para rotación automática
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotate_view)
        self.rotation_timer.start(50)
        
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen", "", 
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_name:
            # Animación del botón
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
            self.update_visualization()
            
    def update_visualization(self):
        if self.image_data is None:
            return
        
        if self.wave_mesh:
            self.gl_widget.removeItem(self.wave_mesh)
        
        amplitude = self.amplitude_slider.slider.value()
        resolution = self.resolution_slider.slider.value()
        
        h, w = self.image_data.shape[:2]
        step_x = max(1, w // resolution)
        step_y = max(1, h // resolution)
        
        x = np.arange(0, w, step_x)
        y = np.arange(0, h, step_y)
        
        # Crear malla de puntos
        points = []
        colors = []
        
        for i, yi in enumerate(y):
            for j, xi in enumerate(x):
                if yi < h and xi < w:
                    color = self.image_data[yi, xi] / 255.0
                    brightness = np.mean(color)
                    
                    # Altura basada en brillo
                    z = brightness * amplitude
                    
                    # Posición centrada
                    px = (xi - w/2) * 0.2
                    py = (yi - h/2) * 0.2
                    
                    points.append([px, py, z])
                    colors.append((*color, 0.9))
        
        points = np.array(points)
        colors = np.array(colors)
        
        # Crear mesh de puntos 3D
        self.wave_mesh = gl.GLScatterPlotItem(
            pos=points,
            color=colors,
            size=3,
            pxMode=True
        )
        
        self.gl_widget.addItem(self.wave_mesh)
        
    def show_fft_analysis(self):
        if self.image_data is None:
            return
        
        # Convertir a escala de grises
        gray = np.mean(self.image_data, axis=2)
        
        # Aplicar FFT 2D
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude = np.abs(fft_shift)
        phase = np.angle(fft_shift)
        
        # Calcular estadísticas
        mean_mag = np.mean(magnitude)
        max_mag = np.max(magnitude)
        energy = np.sum(magnitude ** 2)
        
        # Frecuencias dominantes
        h, w = magnitude.shape
        peak_indices = np.unravel_index(
            np.argsort(magnitude.ravel())[-5:], 
            magnitude.shape
        )
        
        info_text = (
            f"📊 ANÁLISIS FFT 2D\n\n"
            f"Magnitud promedio: {mean_mag:.2e}\n"
            f"Magnitud máxima: {max_mag:.2e}\n"
            f"Energía total: {energy:.2e}\n"
            f"Dimensiones FFT: {h}x{w}\n"
            f"Componentes: {h*w:,}"
        )
        
        self.fft_info.setText(info_text)
        
        # Crear visualización de magnitud FFT
        magnitude_log = np.log(magnitude + 1)
        magnitude_norm = (magnitude_log - magnitude_log.min()) / (magnitude_log.max() - magnitude_log.min())
        
        # Actualizar visualización 3D con FFT
        resolution = self.resolution_slider.slider.value()
        step_x = max(1, w // resolution)
        step_y = max(1, h // resolution)
        
        x = np.arange(0, w, step_x)
        y = np.arange(0, h, step_y)
        
        points = []
        colors = []
        
        for i, yi in enumerate(y):
            for j, xi in enumerate(x):
                if yi < h and xi < w:
                    mag_value = magnitude_norm[yi, xi]
                    
                    px = (xi - w/2) * 0.2
                    py = (yi - h/2) * 0.2
                    pz = mag_value * 50
                    
                    points.append([px, py, pz])
                    
                    # Color basado en magnitud (azul a rojo)
                    color_r = mag_value
                    color_g = 0.3
                    color_b = 1.0 - mag_value
                    colors.append((color_r, color_g, color_b, 0.9))
        
        if self.wave_mesh:
            self.gl_widget.removeItem(self.wave_mesh)
        
        points = np.array(points)
        colors = np.array(colors)
        
        self.wave_mesh = gl.GLScatterPlotItem(
            pos=points,
            color=colors,
            size=4,
            pxMode=True
        )
        
        self.gl_widget.addItem(self.wave_mesh)
        
    def rotate_view(self):
        speed = self.rotation_speed_slider.slider.value()
        if speed > 0 and self.image_data is not None:
            self.rotation_angle += speed * 0.5
            self.gl_widget.setCameraPosition(
                distance=100, 
                elevation=30, 
                azimuth=self.rotation_angle
            )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Configurar fuente global moderna
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = WaveVisualizer()
    window.show()
    sys.exit(app.exec())