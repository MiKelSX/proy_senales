# 🌊✨ Sistema de Visualización 3D de Ondas de Color

> **¡Transforma imágenes en una experiencia 3D única usando FFT!**  
> Interfaz y experiencia 2025: moderna, fluida, responsive y espectacular.

---

## 🚀 Descripción

Esta aplicación convierte cualquier imagen en una visualización 3D de ondas de color, utilizando la **Transformada Rápida de Fourier (FFT)** para analizar y mostrar la intensidad y frecuencia del color en tiempo real. Diseñada con los estándares más modernos de UI, animaciones suaves y controles avanzados.

---

## 🎨 **Diseño de Interfaz**

- **Glassmorphism**: Gradientes vibrantes y transparencias
- **Bordes redondeados** en todos los elementos
- **Animaciones fluidas**: Botones, sliders y transiciones
- **Tema oscuro premium**: Colores neón (azul/morado)
- **Tipografía moderna**: Segoe UI
- **Sombras y profundidad 3D**

<p align="center">
  <img src="https://placehold.co/600x350/222/ccd6ff?text=Demo+3D+Waves" alt="Demo 3D Waves" style="border-radius:20px;box-shadow:0 0 32px #9f5cff;">
</p>

---

## ⚡ **Funcionalidades Principales**

- **Carga de imágenes**: PNG, JPG, JPEG, BMP, GIF
- **Visualización 3D**: Puntos = intensidad de color
- **FFT 2D**: Cálculos detallados y visualización en tiempo real
- **Rotación automática**: Ajustable y controlable
- **Controles interactivos**:
  - Amplitud de onda
  - Resolución de puntos
  - Velocidad de rotación

---

## 📊 **Análisis FFT Avanzado**

- Magnitud promedio y máxima
- Energía total de la señal
- Visualización de frecuencias dominantes
- Transformación en tiempo real

---

## 🆕 **Características Modernas**

### 📱 Responsive Design

- Scroll automático en panel lateral
- Adaptación perfecta a cualquier ventana
- Todos los controles visibles en cualquier tamaño

### 👁️ Panel Ocultable

- Botón entre panel y gráfico (►/◄)
- Visualización 3D a pantalla completa

### 〰️ Animación de Ondas

- Botón Activar/Desactivar (▶/⏸)
- Velocidad ajustable (1-20)
- Selector de dirección (X/Y)
- Efecto sinusoidal suave

### 🔄 Control de Rotación Mejorado

- Play/Pause independiente (▶/⏸)
- Velocidad personalizable (0-20)

### 🔗 Líneas de Conexión

- Botón Mostrar/Ocultar Líneas (◇/◆)
- Malla visual en X (azul) / Y (naranja) / ambas direcciones

### 🎨 Mejoras Visuales

- Estados activo/inactivo en botones
- Animaciones suaves en cambios de estado
- Iconos modernos y secciones organizadas

---

## 🧮 **Ventana de Resultados Matemáticos**

- **Botón "Ver Resultados"** abre ventana independiente
- Cards para cada parámetro con gradientes y bordes redondeados
- Notación matemática real: ℱ, Σ, ∫, μ, σ, φ
- **Resultados**:
  - ℱ{f(x,y)} — Transformada de Fourier 2D
  - μ(|F|), max(|F|), σ(|F|) — Magnitud
  - E = Σ|F|² — Energía total
  - P(u,v) — Potencia espectral
  - SNR (dB) — Relación señal/ruido
  - ⟨φ⟩ — Fase promedio
  - H = -Σp·log₂(p) — Entropía espectral
  - SFM — Planicidad espectral
  - cₓ, cᵧ — Centroide espectral
  - BW — Ancho de banda
  - f_dominant — Frecuencias dominantes

### 📐 **Sección de Ecuaciones Fundamentales**

- Transformada Inversa
- Teorema de Parseval
- Magnitud y Fase
- Potencia y Energía

---

## 🏆 **Optimización Total**

- Renderizado OpenGL nativo (PyQt6)
- Sin lag (numpy optimizado)
- Grid 3D moderno con transparencias
- Actualización eficiente de malla

---

## 🖥️ **Requisitos Técnicos**

- Python 3.10+
- PyQt6
- numpy
- Pillow
- pyqtgraph
- PyOpenGL

---

## ✨ **Instalación y Ejecución**

```bash
git clone https://github.com/MiKelSX/proy_senales.git
cd proy_senales
pip install PyQt6 numpy Pillow pyqtgraph PyOpenGL
python app.py
```

---

## 📸 **Demo**

<p align="center">
  <img src="https://placehold.co/600x350/222/9f5cff?text=FFT+Results+Window" alt="FFT Results Window" style="border-radius:20px;box-shadow:0 0 32px #9f5cff;">
</p>

---

## 🤝 **Contribuciones**

¡Las contribuciones son bienvenidas!  
Por favor, abre un issue o pull request para sugerencias, mejoras o reporte de errores.

---

## 📄 **Licencia**

MIT © [MiKelSX](https://github.com/MiKelSX)

---

<p align="center">
  <b>¡Explora el color, la frecuencia y la matemática en 3D con estilo moderno y fluido! 🚀✨</b>
</p>
