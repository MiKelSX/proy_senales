@echo off
title WaveVisualizer3D - Build Script
color 0B

echo ==================================================
echo   🚀 WaveVisualizer3D - Build EXE Profesional
echo ==================================================
echo.

REM 1. Verificar Python
echo 🔍 Verificando Python...
python --version || (
    echo ❌ Python no está instalado o no está en el PATH.
    pause
    exit /b
)

echo 🔍 Verificando PyInstaller...
pyinstaller --version || (
    echo 🛠 Instalando PyInstaller...
    pip install pyinstaller
)

echo.

REM 2. Limpiar compilaciones previas
echo 🧹 Eliminando carpetas previas build/ y dist/ ...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist WaveVisualizer3D.spec del /q WaveVisualizer3D.spec

echo.

REM 3. Crear WaveVisualizer3D.spec
echo 🛠 Generando archivo WaveVisualizer3D.spec...

echo # -*- mode: python ; coding: utf-8 -*- > WaveVisualizer3D.spec
echo from PyInstaller.utils.hooks import collect_all >> WaveVisualizer3D.spec
echo import site >> WaveVisualizer3D.spec
echo import os >> WaveVisualizer3D.spec
echo. >> WaveVisualizer3D.spec

echo site_packages = site.getsitepackages()[0] >> WaveVisualizer3D.spec
echo datas = [(os.path.join(site_packages, "pyqtgraph"), "pyqtgraph")] >> WaveVisualizer3D.spec
echo binaries = [] >> WaveVisualizer3D.spec
echo hiddenimports = [] >> WaveVisualizer3D.spec
echo. >> WaveVisualizer3D.spec

echo tmp = collect_all('PyQt6') >> WaveVisualizer3D.spec
echo datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2] >> WaveVisualizer3D.spec

echo tmp = collect_all('pyqtgraph') >> WaveVisualizer3D.spec
echo datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2] >> WaveVisualizer3D.spec

echo tmp = collect_all('OpenGL') >> WaveVisualizer3D.spec
echo datas += tmp[0]; binaries += tmp[1]; hiddenimports += tmp[2] >> WaveVisualizer3D.spec

echo. >> WaveVisualizer3D.spec
echo a = Analysis(['app.py'], pathex=[], binaries=binaries, datas=datas, hiddenimports=hiddenimports, hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False, optimize=0) >> WaveVisualizer3D.spec
echo pyz = PYZ(a.pure) >> WaveVisualizer3D.spec

echo exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='WaveVisualizer3D', debug=False, bootloader_ignore_signals=False, strip=False, upx=False, upx_exclude=[], runtime_tmpdir=None, console=False) >> WaveVisualizer3D.spec

echo ✔ Archivo .spec generado.
echo.

REM 4. Compilar EXE
echo 🔨 Compilando ejecutable...
pyinstaller WaveVisualizer3D.spec

IF %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: La compilación falló.
    echo Revisa el log arriba.
    pause
    exit /b
)

echo.
echo ==================================================
echo   ✔ COMPILACIÓN COMPLETA
echo   El ejecutable está en:
echo   dist\WaveVisualizer3D.exe
echo ==================================================
echo.

explorer dist
pause
