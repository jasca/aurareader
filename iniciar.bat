@echo off
setlocal enabledelayedexpansion
echo ==========================================
echo ✨ Iniciando AuraReader Kiosco V2.0 (Windows)
echo ==========================================

cd /d "%~dp0"

:: 1. Detectar ejecutable de Python disponible en Windows
set "PYTHON_CMD="

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
) else (
    py --version >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_CMD=py"
    )
)

if "%PYTHON_CMD%"=="" (
    echo.
    echo ❌ ERROR: No se encontró Python en el sistema o no está en las variables PATH.
    echo.
    echo 📌 Por favor descarga e instala Python desde: https://www.python.org/downloads/
    echo ⚠️ IMPORTANTE: Durante la instalación, marca la casilla "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

echo Usando ejecutable de Python: %PYTHON_CMD%

:: 2. Crear entorno virtual si no existe
if not exist "venv" (
    echo Creando entorno virtual e instalando dependencias...
    %PYTHON_CMD% -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

:: 3. Iniciar servidor backend
echo Iniciando servidor backend...
start /b python -m backend.main

timeout /t 3 /nobreak > nul

:: 4. Abrir interfaz en navegador
echo Abriendo interfaz en el navegador...
start http://localhost:8000/frontend/index.html

echo ==========================================
echo ✅ AuraReader listo para operar.
echo ==========================================
