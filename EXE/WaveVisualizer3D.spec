# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import importlib
import os

# Ruta real de pyqtgraph usando importlib
pg_module = importlib.import_module("pyqtgraph")
pg_path = os.path.dirname(pg_module.__file__)

datas = [(pg_path, "pyqtgraph")]
binaries = []
hiddenimports = []

# Añadir PyQt6
tmp = collect_all('PyQt6')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

# Añadir pyqtgraph completo
tmp = collect_all('pyqtgraph')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

# Añadir OpenGL
tmp = collect_all('OpenGL')
datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='WaveVisualizer3D',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
