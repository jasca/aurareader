@echo off
setlocal enabledelayedexpansion
echo ==========================================
echo ✨ Iniciando AuraReader Kiosco V2.0 (Windows)
echo ==========================================

cd /d "%~dp0"

set "PYTHON_CMD="

:: 1. Probar el lanzador nativo de Windows para Python 3 (py -3)
py -3 -c "import sys; exit(0 if sys.version_info[0] >= 3 else 1)" >nul 2>&1
if !errorlevel! equ 0 (
    set "PYTHON_CMD=py -3"
    goto :PYTHON_FOUND
)

:: 2. Probar si 'python' es Python 3
python -c "import sys; exit(0 if sys.version_info[0] >= 3 else 1)" >nul 2>&1
if !errorlevel! equ 0 (
    set "PYTHON_CMD=python"
    goto :PYTHON_FOUND
)

:: 3. Buscar instalaciones de Python 3 en carpetas comunes de Windows
for /d %%d in ("%LocalAppData%\Programs\Python\Python3*") do (
    if exist "%%d\python.exe" (
        set "PYTHON_CMD=%%d\python.exe"
        goto :PYTHON_FOUND
    )
)

for /d %%d in ("C:\Python3*") do (
    if exist "%%d\python.exe" (
        set "PYTHON_CMD=%%d\python.exe"
        goto :PYTHON_FOUND
    )
)

:PYTHON_FOUND
if "%PYTHON_CMD%"=="" (
    echo.
    echo ❌ ERROR: Se detectó Python 2.7 (C:\Python27\python.exe), pero AuraReader requiere Python 3.
    echo.
    echo 📌 Por favor instala Python 3 (3.10 / 3.11 / 3.12) desde:
    echo    👉 https://www.python.org/downloads/
    echo.
    echo ⚠️ IMPORTANTE: Durante la instalación en Windows, marca la casilla:
    echo    [x] Add python.exe to PATH
    echo.
    pause
    exit /b 1
)

echo Usando ejecutable de Python 3: %PYTHON_CMD%

:: Si existe un entorno venv viejo creado con Python 2, borrarlo para re-crear en Python 3
if exist "venv" (
    if not exist "venv\Scripts\pip.exe" (
        rmdir /s /q venv
    )
)

:: Crear entorno virtual si no existe
if not exist "venv" (
    echo Creando entorno virtual Python 3 e instalando dependencias...
    %PYTHON_CMD% -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo Iniciando servidor backend...
start /b python -m backend.main

timeout /t 3 /nobreak > nul

echo Abriendo interfaz en el navegador...
start http://localhost:8000/frontend/index.html

echo ==========================================
echo ✅ AuraReader listo para operar.
echo ==========================================
