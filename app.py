import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QSlider, 
                             QHBoxLayout, QFrame, QGraphicsDropShadowEffect, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint
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
        self.show_lines = False
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
        
        # Toggle de líneas de conexión
        self.lines_toggle = ToggleButton("Mostrar Líneas", "Ocultar Líneas", "◇", "◆")
        self.lines_toggle.clicked.connect(self.toggle_lines)
        
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
        
        # Botón de análisis FFT
        self.fft_btn = AnimatedButton("⚡ Análisis FFT")
        self.fft_btn.clicked.connect(self.show_fft_analysis)
        self.fft_btn.setEnabled(False)
        
        # Info FFT
        self.fft_info = QLabel("")
        self.fft_info.setStyleSheet("""
            QLabel {
                color: #6478FF;
                font-size: 11px;
                font-family: 'Consolas', monospace;
                background: #1E1E2E;
                padding: 12px;
                border-radius: 12px;
                border: 2px solid #6478FF;
            }
        """)
        self.fft_info.setWordWrap(True)
        
        control_layout.addWidget(title)
        control_layout.addWidget(self.load_btn)
        control_layout.addWidget(self.info_label)
        control_layout.addWidget(viz_label)
        control_layout.addWidget(self.amplitude_slider)
        control_layout.addWidget(self.resolution_slider)
        control_layout.addWidget(self.lines_toggle)
        control_layout.addWidget(rot_label)
        control_layout.addWidget(self.rotation_toggle)
        control_layout.addWidget(self.rotation_speed_slider)
        control_layout.addWidget(wave_label)
        control_layout.addWidget(self.wave_toggle)
        control_layout.addWidget(self.wave_speed_slider)
        control_layout.addWidget(self.wave_direction_slider)
        control_layout.addWidget(self.fft_btn)
        control_layout.addWidget(self.fft_info)
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
        
    def toggle_lines(self):
        self.show_lines = self.lines_toggle.toggle()
        self.update_visualization()
        
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
        
        for i, yi in enumerate(y_coords):
            for j, xi in enumerate(x_coords):
                if yi < h and xi < w:
                    color = self.image_data[int(yi), int(xi)] / 255.0
                    brightness = np.mean(color)
                    
                    # Aplicar animación de ondas
                    wave_effect = 0
                    if self.wave_animation_active:
                        direction = self.wave_direction_slider.slider.value()
                        if direction == 0:  # Animación en X
                            wave_effect = np.sin((xi * 0.05) + self.wave_offset) * 3
                        else:  # Animación en Y
                            wave_effect = np.sin((yi * 0.05) + self.wave_offset) * 3
                    
                    z = brightness * amplitude + wave_effect
                    
                    px = (xi - w/2) * 0.2
                    py = (yi - h/2) * 0.2
                    
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
        
        # Crear líneas de conexión si está activado
        if self.show_lines:
            # Líneas en dirección X
            for i in range(len(y_coords)):
                line_points = []
                for j in range(len(x_coords)):
                    if (i, j) in point_grid:
                        line_points.append(point_grid[(i, j)])
                
                if len(line_points) > 1:
                    line_points = np.array(line_points)
                    line = gl.GLLinePlotItem(
                        pos=line_points,
                        color=(0.4, 0.5, 1.0, 0.6),
                        width=1.5,
                        antialias=True
                    )
                    self.gl_widget.addItem(line)
                    self.wave_lines.append(line)
            
            # Líneas en dirección Y
            for j in range(len(x_coords)):
                line_points = []
                for i in range(len(y_coords)):
                    if (i, j) in point_grid:
                        line_points.append(point_grid[(i, j)])
                
                if len(line_points) > 1:
                    line_points = np.array(line_points)
                    line = gl.GLLinePlotItem(
                        pos=line_points,
                        color=(1.0, 0.5, 0.4, 0.6),
                        width=1.5,
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
        
        mean_mag = np.mean(magnitude)
        max_mag = np.max(magnitude)
        energy = np.sum(magnitude ** 2)
        
        h, w = magnitude.shape
        
        info_text = (
            f"📊 ANÁLISIS FFT 2D\n\n"
            f"Magnitud promedio: {mean_mag:.2e}\n"
            f"Magnitud máxima: {max_mag:.2e}\n"
            f"Energía total: {energy:.2e}\n"
            f"Dimensiones: {h}x{w}\n"
            f"Componentes: {h*w:,}"
        )
        
        self.fft_info.setText(info_text)
        
        magnitude_log = np.log(magnitude + 1)
        magnitude_norm = (magnitude_log - magnitude_log.min()) / (magnitude_log.max() - magnitude_log.min())
        
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