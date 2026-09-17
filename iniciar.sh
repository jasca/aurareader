#!/bin/bash

# Directorio base de AuraReader
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================="
echo "✨ Iniciando AuraReader Kiosco V2.0"
echo "=========================================="

# 0. Verificar e instanciar entorno virtual si no existe
if [ ! -d "$DIR/venv" ]; then
    echo "Creando entorno virtual e instalando dependencias..."
    python3 -m venv "$DIR/venv"
    "$DIR/venv/bin/pip" install --upgrade pip
    "$DIR/venv/bin/pip" install -r "$DIR/requirements.txt"
fi

# 1. Liberar puerto 8000 de cualquier proceso anterior
echo "Limpiando puerto 8000..."
lsof -ti:8000 | xargs kill -9 > /dev/null 2>&1 || true
fuser -k 8000/tcp > /dev/null 2>&1 || true
pkill -f "backend.main" > /dev/null 2>&1 || true
sleep 1

# 2. Iniciar el servidor backend en segundo plano
echo "Iniciando servidor local..."
"$DIR/venv/bin/python3" -m backend.main > "$DIR/backend.log" 2>&1 &

SERVER_PID=$!
echo "Servidor iniciado en PID $SERVER_PID"

# Esperar a que el servidor responda
echo "Verificando disponibilidad del servidor..."
for i in {1..10}; do
    if curl -s http://127.0.0.1:8000/frontend/index.html > /dev/null; then
        echo "✅ Servidor respondiendo en http://127.0.0.1:8000"
        break
    fi
    sleep 0.5
done

# 3. Abrir el navegador en el kiosco
echo "Abriendo interfaz en el navegador..."
if command -v google-chrome &> /dev/null; then
    google-chrome --start-fullscreen --app="http://127.0.0.1:8000/frontend/index.html" &
elif command -v chromium-browser &> /dev/null; then
    chromium-browser --start-fullscreen --app="http://127.0.0.1:8000/frontend/index.html" &
elif command -v firefox &> /dev/null; then
    firefox --kiosk "http://127.0.0.1:8000/frontend/index.html" &
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://127.0.0.1:8000/frontend/index.html" &
fi

echo "=========================================="
echo "✅ AuraReader listo para operar."
echo "Accede manualmente en tu navegador: http://127.0.0.1:8000/frontend/index.html"
echo "=========================================="

