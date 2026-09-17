# 📖 Guía Rápida para el Operador del Stand - AuraReader V2.0

Esta guía está pensada para que **cualquier persona a cargo del stand** pueda iniciar, reiniciar o resolver cualquier problema en **AuraReader** en menos de 1 minuto, sin necesidad de conocimientos técnicos.

---

## 🚀 OPCIÓN 1: Inicio Rápido en 1 Clic (Recomendado)

1. Abre la carpeta `3_AuraReader`.
2. Haz doble clic en el archivo **`iniciar.sh`** (o ejecútalo en la terminal).
3. ¡Listo! Se abrirá automáticamente el sistema en la pantalla completa del navegador listo para usar.

---

## 💻 OPCIÓN 2: Inicio Manual por Terminal (Paso a Paso)

Si prefieres iniciarlo desde la terminal:

### Paso 1: Abrir la terminal y navegar a la carpeta
```bash
cd /home/alejasca/Laboratorios/Demo_Congreso_Lanus/3_AuraReader
```

### Paso 2: Ejecutar el script de inicio
```bash
./iniciar.sh
```

---

## 🌐 OPCIÓN 3: Si el navegador ya está abierto pero muestra error

1. Abre cualquier navegador (Google Chrome, Firefox o Edge).
2. Ingresa a la siguiente dirección en la barra de direcciones:
   ```text
   http://localhost:8000/frontend/index.html
   ```
3. Presiona `Enter` y presiona la tecla `F11` para poner la pantalla completa.

---

## 🛠️ ¿Qué hacer si algo se traba o no responde? (Reinicio Forzado)

Si la cámara se traba o la pantalla queda en negro:

1. **Cierra la ventana del navegador**.
2. Abre una terminal y ejecuta este comando para reiniciar todo de cero:
   ```bash
   cd /home/alejasca/Laboratorios/Demo_Congreso_Lanus/3_AuraReader
   ./iniciar.sh
   ```
3. El script cerrará los procesos viejos y abrirá el sistema totalmente limpio en 2 segundos.

---

## 📋 Pasos para Atender a un Consultante en el Stand

1. **Cargar los Datos**:
   - Pide e ingresa **Nombre y Apellido** *(Obligatorio)*.
   - Pide e ingresa **Número de Celular** con código de área (ej: `5491112345678`) *(Obligatorio)*.
   - Email *(Opcional)*.
2. **Seleccionar Servicio**:
   - Haz clic en **"✨ Iniciar Escáner de Aura"** o **"🔋 Iniciar Análisis Biorritmo"**.
3. **Indicaciones al Consultante**:
   - Pídele a la persona que se ubique frente a la cámara web.
   - Para Aura: La voz le indicará realizar **2 inhalaciones y 2 exhalaciones**.
   - Para Biorritmo: Verá una cuenta regresiva (3.. 2.. 1) y se tomará la captura.
4. **Entrega del Reporte**:
   - En pantalla aparecerá la fotografía energética y la sugerencia de Sahumerio.
   - Pide al consultante que enfoque la cámara de su celular al **Código QR** en pantalla para abrir el chat de WhatsApp con su reporte PDF listo.
5. **Finalizar**:
   - Presiona el botón **"Finalizar y Volver"** para dejar el quiosco listo para la siguiente persona.
