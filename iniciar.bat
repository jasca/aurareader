@echo off
echo ==========================================
echo ✨ Iniciando AuraReader Kiosco V2.0 (Windows)
echo ==========================================

cd /d "%~dp0"

IF NOT EXIST "venv" (
    echo Creando entorno virtual e instalando dependencias...
    python -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate.bat
)

echo Iniciando servidor backend...
start /b python -m backend.main

timeout /t 2 /nobreak > NUL

echo Abriendo interfaz en el navegador...
start http://localhost:8000/frontend/index.html

echo ==========================================
echo ✅ AuraReader listo para operar.
echo ==========================================
