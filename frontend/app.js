document.addEventListener('DOMContentLoaded', async () => {
    // UI Elements
    const videoElement = document.getElementById('input_video');
    const canvasElement = document.getElementById('output_canvas');
    const canvasCtx = canvasElement.getContext('2d');
    const tempCanvas = document.getElementById('temp_canvas');
    const tempCtx = tempCanvas.getContext('2d');
    
    // Contenedores
    const mainMenuContainer = document.getElementById('mainMenuContainer');
    const biorhythmForm = document.getElementById('biorhythmForm');
    const breathingUI = document.getElementById('breathingUI');
    const resultsContainer = document.getElementById('resultsContainer');
    const breathText = document.getElementById('breathText');
    const breathCircle = document.getElementById('breathCircle');
    
    // Botones
    const btnMenuAura = document.getElementById('btnMenuAura');
    const btnMenuBiorhythm = document.getElementById('btnMenuBiorhythm');
    const btnStartBiorhythm = document.getElementById('btnStartBiorhythm');
    const resetBtn = document.getElementById('resetBtn');
    
    // Resultados
    const statusText = document.getElementById('statusText');
    const capturedImage = document.getElementById('capturedImage');
    const analysisText = document.getElementById('analysisText');
    const biorhythmPhrase = document.getElementById('biorhythmPhrase');
    const productsGrid = document.getElementById('productsGrid');
    const waQrCode = document.getElementById('waQrCode');
    const resultsTitle = document.getElementById('resultsTitle');

    // Variables de Estado
    let currentMode = null; // 'AURA' o 'BIORHYTHM'
    let isScanning = false;
    let isFrozen = false;
    let isCameraRunning = false;
    let currentColorHex = '#34d399'; 
    let collectedEmotions = { happy: 0, neutral: 0, angry: 0, sad: 0, fearful: 0 };
    let emotionFramesCount = 0;
    
    // Cámara y Dispositivos
    const cameraSelect = document.getElementById('cameraSelect');
    let currentStream = null;
    let animFrameId = null;
    let isProcessingFrame = false;
    
    // Buffers estáticos para la máscara y la persona
    let staticMask = document.createElement('canvas');
    let staticPerson = document.createElement('canvas');

    async function populateCameraDevices() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;
        try {
            let devices = await navigator.mediaDevices.enumerateDevices();
            let videoDevices = devices.filter(d => d.kind === 'videoinput');
            
            // Si las etiquetas están vacías, solicitar permiso preliminar para leer los nombres de las cámaras
            if (videoDevices.length > 0 && !videoDevices[0].label) {
                try {
                    const tempStream = await navigator.mediaDevices.getUserMedia({ video: true });
                    tempStream.getTracks().forEach(t => t.stop());
                    devices = await navigator.mediaDevices.enumerateDevices();
                    videoDevices = devices.filter(d => d.kind === 'videoinput');
                } catch (permErr) {
                    console.warn("Permiso de cámara preliminar no otorgado:", permErr);
                }
            }

            cameraSelect.innerHTML = '';
            
            // Opción por defecto (Universal)
            const defaultOpt = document.createElement('option');
            defaultOpt.value = '';
            defaultOpt.text = '📷 Cámara Predeterminada / DroidCam';
            cameraSelect.appendChild(defaultOpt);

            let selectedIndex = 0; // Por defecto la opción universal
            videoDevices.forEach((device, index) => {
                const opt = document.createElement('option');
                opt.value = device.deviceId;
                const label = device.label || `Cámara ${index + 1}`;
                opt.text = label;
                cameraSelect.appendChild(opt);

                const lower = label.toLowerCase();
                if (lower.includes('droidcam') || lower.includes('loopback') || lower.includes('dummy') || lower.includes('v4l2')) {
                    selectedIndex = index + 1; // +1 por la opción default
                }
            });
            cameraSelect.selectedIndex = selectedIndex;
        } catch (err) {
            console.error("Error al enumerar cámaras:", err);
        }
    }

    populateCameraDevices();
    if (navigator.mediaDevices) {
        navigator.mediaDevices.addEventListener('devicechange', populateCameraDevices);
    }

    function resizeCanvas() {
        canvasElement.width = window.innerWidth; canvasElement.height = window.innerHeight;
        tempCanvas.width = window.innerWidth; tempCanvas.height = window.innerHeight;
        staticMask.width = window.innerWidth; staticMask.height = window.innerHeight;
        staticPerson.width = window.innerWidth; staticPerson.height = window.innerHeight;
        
        if (!isCameraRunning) {
            canvasCtx.fillStyle = '#000000';
            canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        }
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    // Audios
    const ttsInicio = new Audio('assets/inicio.mp3');
    const ttsInhala = new Audio('assets/inhala.mp3');
    const ttsExhala = new Audio('assets/exhala.mp3');
    const tibetanBowl = new Audio('assets/campana.wav');
    function playAudio(audioObj) { audioObj.currentTime = 0; audioObj.play().catch(e => console.error("Audio bloqueado:", e)); }

    // Inicialización de IA
    const selfieSegmentation = new SelfieSegmentation({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/selfie_segmentation/${file}`
    });
    selfieSegmentation.setOptions({ modelSelection: 1 });
    selfieSegmentation.onResults(onResults);

    async function loadModels() {
        try {
            await faceapi.nets.tinyFaceDetector.loadFromUri('https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/');
            await faceapi.nets.faceExpressionNet.loadFromUri('https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/');
            await selfieSegmentation.initialize();
            
            btnMenuAura.disabled = false; btnMenuBiorhythm.disabled = false;
            btnMenuAura.innerText = "✨ Iniciar Escáner de Aura"; btnMenuBiorhythm.innerText = "🔋 Iniciar Análisis Biorritmo";
            statusText.innerText = "Sistema Listo. Esperando selección.";
            statusText.style.color = "#34d399";
        } catch (e) {
            console.error("Error cargando modelos:", e);
            statusText.innerText = "Error cargando IA.";
            statusText.style.color = "#ef4444";
        }
    }
    loadModels();

    async function startCameraIfNeeded(callback) {
        if (isCameraRunning) {
            if(callback) callback();
            return;
        }
        breathText.innerText = "Conectando Cámara...";
        breathCircle.className = "breath-circle";
        breathingUI.classList.remove('hidden');
        
        const selectedDeviceId = cameraSelect ? cameraSelect.value : '';

        const tryGetUserMedia = async (deviceId) => {
            // 1. Intentar con deviceId preferido e ideal resolución
            try {
                const constraints = deviceId
                    ? { video: { deviceId: { ideal: deviceId }, width: { ideal: 1280 }, height: { ideal: 720 } } }
                    : { video: { width: { ideal: 1280 }, height: { ideal: 720 } } };
                return await navigator.mediaDevices.getUserMedia(constraints);
            } catch (e1) {
                console.warn("Intento 1 de cámara falló:", e1);
            }

            // 2. Intentar solo con deviceId preferido sin restricciones de resolución
            try {
                const constraints = deviceId
                    ? { video: { deviceId: { ideal: deviceId } } }
                    : { video: true };
                return await navigator.mediaDevices.getUserMedia(constraints);
            } catch (e2) {
                console.warn("Intento 2 de cámara falló:", e2);
            }

            // 3. Fallback universal total (cualquier cámara disponible sin ID estricto)
            console.warn("Usando fallback universal { video: true }");
            return await navigator.mediaDevices.getUserMedia({ video: true });
        };

        try {
            if (currentStream) {
                currentStream.getTracks().forEach(t => t.stop());
            }
            currentStream = await tryGetUserMedia(selectedDeviceId);
            videoElement.srcObject = currentStream;
            await videoElement.play();
            isCameraRunning = true;

            runFrameLoop();
            if(callback) callback();
        } catch (err) {
            console.error("Error al iniciar cámara/DroidCam:", err);
            alert("No se pudo iniciar la cámara (DroidCam). Verifica que la app DroidCam esté abierta y activa en Linux.");
            breathingUI.classList.add('hidden');
            resetToMenu();
        }
    }

    function runFrameLoop() {
        if (animFrameId) cancelAnimationFrame(animFrameId);
        
        async function processFrame() {
            if (!isCameraRunning) return;
            if (!isFrozen && !isProcessingFrame && videoElement.readyState >= 2) {
                isProcessingFrame = true;
                try {
                    await selfieSegmentation.send({ image: videoElement });
                } catch (e) {
                    console.error("Error procesando frame:", e);
                }
                isProcessingFrame = false;
            }
            if (isCameraRunning) {
                animFrameId = requestAnimationFrame(processFrame);
            }
        }
        processFrame();
    }

    // Algoritmo para expandir máscara acotada (Requerimiento 3: 2-3 cm de silueta)
    function createExpandedMask(baseImg, radius) {
        const c = document.createElement('canvas');
        c.width = canvasElement.width; c.height = canvasElement.height;
        const cx = c.getContext('2d');
        const steps = 16;
        for (let i = 0; i < steps; i++) {
            const angle = (i * 2 * Math.PI) / steps;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            cx.drawImage(baseImg, x, y);
        }
        return c;
    }

    // RENDERIZADO EN VIVO
    function onResults(results) {
        if (isFrozen) return;

        // Guardar buffers de máscara y persona
        const maskCtx = staticMask.getContext('2d');
        maskCtx.clearRect(0, 0, staticMask.width, staticMask.height);
        maskCtx.filter = 'blur(4px)';
        maskCtx.drawImage(results.segmentationMask, 0, 0, staticMask.width, staticMask.height);
        maskCtx.filter = 'none';

        const personCtx = staticPerson.getContext('2d');
        personCtx.clearRect(0, 0, staticPerson.width, staticPerson.height);
        personCtx.drawImage(results.segmentationMask, 0, 0, staticPerson.width, staticPerson.height);
        personCtx.globalCompositeOperation = 'source-in';
        personCtx.drawImage(results.image, 0, 0, staticPerson.width, staticPerson.height);
        personCtx.globalCompositeOperation = 'source-over';

        canvasCtx.save();
        // Fondo 100% negro
        canvasCtx.fillStyle = '#000000';
        canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);

        // REQUERIMIENTO 2: SE ELIMINÓ EL ÓVALO PUNTEADO

        // REQUERIMIENTO 3: Halo del aura limitado a 2-3 cm (30px) sobre la silueta
        if (currentMode === 'AURA') {
            const expandedAuraMask = createExpandedMask(staticMask, 28);
            
            tempCtx.save();
            tempCtx.clearRect(0, 0, tempCanvas.width, tempCanvas.height);
            tempCtx.drawImage(expandedAuraMask, 0, 0);
            tempCtx.globalCompositeOperation = 'source-in';
            tempCtx.fillStyle = currentColorHex;
            tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
            tempCtx.restore();

            canvasCtx.save();
            canvasCtx.globalCompositeOperation = 'screen';
            canvasCtx.filter = 'blur(18px)';
            canvasCtx.drawImage(tempCanvas, 0, 0);
            canvasCtx.filter = 'blur(8px)';
            canvasCtx.drawImage(tempCanvas, 0, 0);
            canvasCtx.restore();
        } 
        
        // Dibujamos a la persona sobre el fondo/aura
        canvasCtx.globalCompositeOperation = 'source-over';
        canvasCtx.drawImage(staticPerson, 0, 0);
        
        canvasCtx.restore();
    }

    // NAVEGACIÓN Y FLUJOS
    btnMenuAura.addEventListener('click', () => {
        if (isScanning) return;
        const userName = document.getElementById('userName').value.trim();
        const userPhone = document.getElementById('userPhone').value.trim();
        if (!userName) { alert("Por favor, ingresa tu Nombre y Apellido."); return; }
        if (!userPhone) { alert("Por favor, ingresa tu celular para recibir el reporte."); return; }
        
        currentMode = 'AURA';
        biorhythmForm.classList.add('hidden');
        mainMenuContainer.classList.add('hidden');
        
        startCameraIfNeeded(() => {
            beginAuraScan();
        });
    });

    btnMenuBiorhythm.addEventListener('click', () => {
        currentMode = 'BIORHYTHM';
        biorhythmForm.classList.remove('hidden');
    });

    let emotionInterval = null;

    function beginAuraScan() {
        isScanning = true;
        collectedEmotions = { happy: 0, neutral: 0, angry: 0, sad: 0, fearful: 0, disgusted: 0, surprised: 0 };
        emotionFramesCount = 0;

        if (emotionInterval) clearInterval(emotionInterval);

        emotionInterval = setInterval(async () => {
            if (isFrozen || !isCameraRunning) { clearInterval(emotionInterval); return; }
            try {
                const detections = await faceapi.detectSingleFace(videoElement, new faceapi.TinyFaceDetectorOptions()).withFaceExpressions();
                if (detections && detections.expressions) {
                    Object.keys(collectedEmotions).forEach(key => {
                        const val = detections.expressions[key];
                        // Solo sumar si supera el umbral de ruido de cámara (0.25)
                        if (val && val > 0.25) {
                            collectedEmotions[key] += val;
                        }
                    });
                    emotionFramesCount++;
                }
            } catch (e) {
                // Ignore detector errors
            }
        }, 500);

        let cycleCount = 0;
        playAudio(ttsInicio);
        
        setTimeout(() => {
            function doBreathCycle() {
                // REQUERIMIENTO 1: Exactamente 2 inhalaciones y 2 exhalaciones
                if (cycleCount >= 2) {
                    if (emotionInterval) clearInterval(emotionInterval);
                    finishAuraScan();
                    return;
                }
                playAudio(tibetanBowl);
                setTimeout(() => playAudio(ttsInhala), 300); 
                breathText.innerText = "Inhala...";
                breathCircle.className = "breath-circle inhale";
                
                setTimeout(() => {
                    playAudio(ttsExhala);
                    breathText.innerText = "Exhala...";
                    breathCircle.className = "breath-circle exhale";
                    setTimeout(() => { cycleCount++; doBreathCycle(); }, 4000);
                }, 4000);
            }
            doBreathCycle();
        }, 3000);
    }

    btnStartBiorhythm.addEventListener('click', async () => {
        if (isScanning) return;
        const userName = document.getElementById('userName').value.trim();
        const userPhone = document.getElementById('userPhone').value.trim();
        if (!userName) { alert("Por favor, ingresa tu Nombre y Apellido."); return; }
        if (!userPhone) { alert("Por favor, ingresa tu celular para recibir el reporte."); return; }
        const birthdate = document.getElementById('biorhythmDate').value;
        if (!birthdate) { alert("Por favor, ingresa tu fecha de nacimiento."); return; }
        
        mainMenuContainer.classList.add('hidden');
        startCameraIfNeeded(() => {
            isScanning = true;
            biorhythmForm.classList.add('hidden'); 
            breathingUI.classList.add('hidden'); 
            
            const countdownUI = document.getElementById('countdownUI');
            const countdownText = document.getElementById('countdownText');
            countdownUI.classList.remove('hidden');
            
            let count = 3;
            countdownText.innerText = count;
            playAudio(tibetanBowl);
            
            const countInterval = setInterval(() => {
                count--;
                if (count > 0) {
                    countdownText.innerText = count;
                } else {
                    clearInterval(countInterval);
                    countdownUI.classList.add('hidden');
                    
                    // CALCULAR BIORRITMO LOCALMENTE PARA ANILLOS
                    const bDate = new Date(birthdate);
                    const today = new Date();
                    const diffTime = Math.abs(today - bDate);
                    const diasTotales = Math.floor(diffTime / (1000 * 60 * 60 * 24));
                    
                    const calcDay = (dias, p) => Math.round(((Math.sin(2 * Math.PI * dias / p) + 1) / 2) * 100);
                    
                    const f = calcDay(diasTotales, 23);
                    const e = calcDay(diasTotales, 28);
                    const intl = calcDay(diasTotales, 33);
                    const s = calcDay(diasTotales, 53);
                    
                    isFrozen = true;
                    drawBiorhythmRings({fisico: f, emocional: e, intelectual: intl, espiritual: s});
                    
                    const sessionId = "S" + Date.now().toString(36).toUpperCase();
                    const userEmail = document.getElementById('userEmail').value.trim();

                    setTimeout(() => {
                        doFlashAndCapture('/api/biorhythm', { 
                            name: userName,
                            phone_number: userPhone,
                            email: userEmail,
                            birthdate: birthdate, 
                            period: 'today',
                            session_id: sessionId
                        }, showBiorhythmResults);
                    }, 100);
                }
            }, 1000);
        });
    });

    async function finishAuraScan() {
        if (emotionInterval) clearInterval(emotionInterval);
        breathingUI.classList.add('hidden');
        isScanning = false;
        
        const auraColors = [
            "#a855f7", // Violeta (Espiritualidad)
            "#ec4899", // Rosa (Amor y Alegría)
            "#34d399", // Verde (Sanación y Equilibrio)
            "#fef08a", // Amarillo (Intelecto y Luz)
            "#3b82f6", // Azul (Calma y Paz)
            "#ef4444", // Rojo (Pasión y Fuerza)
            "#451a03"  // Marrón (Enraizamiento)
        ];
        
        let dominantEmotion = "neutral";
        let maxVal = 0;
        if (emotionFramesCount > 0) {
            for (let [emo, val] of Object.entries(collectedEmotions)) {
                if (emo !== "neutral" && val > maxVal) { 
                    maxVal = val; 
                    dominantEmotion = emo; 
                }
            }
        }
        
        if (dominantEmotion === "happy" && maxVal > 0.5) currentColorHex = "#ec4899"; // Rosa
        else if (dominantEmotion === "angry" && maxVal > 0.5) currentColorHex = "#ef4444"; // Rojo
        else if (dominantEmotion === "sad" && maxVal > 0.5) currentColorHex = "#451a03"; // Marrón
        else if (dominantEmotion === "surprised" && maxVal > 0.5) currentColorHex = "#fef08a"; // Amarillo
        else if (dominantEmotion === "fearful" && maxVal > 0.5) currentColorHex = "#a855f7"; // Violeta
        else if (dominantEmotion === "disgusted" && maxVal > 0.5) currentColorHex = "#34d399"; // Verde
        else {
            // Si la emoción es serena/neutral, seleccionar el color de aura basado en el hash del nombre y momento
            const userName = document.getElementById('userName').value.trim() || "Consultante";
            const seed = (userName + Date.now().toString()).split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
            currentColorHex = auraColors[seed % auraColors.length];
        }

        setTimeout(() => {
            const userName = document.getElementById('userName').value.trim();
            const userPhone = document.getElementById('userPhone').value.trim();
            const userEmail = document.getElementById('userEmail').value.trim();
            const sessionId = "A" + Date.now().toString(36).toUpperCase();

            doFlashAndCapture('/api/analyze', { 
                name: userName,
                phone_number: userPhone,
                email: userEmail,
                aura_color_hex: currentColorHex,
                session_id: sessionId
            }, showAuraResults);
        }, 200);
    }

    // CAPTURA Y ENVÍO AL BACKEND
    function doFlashAndCapture(endpoint, payload, callback) {
        isFrozen = true;
        const flash = document.createElement('div');
        flash.className = 'flash-effect';
        document.body.appendChild(flash);
        setTimeout(() => flash.remove(), 1000);

        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'aiLoadingOverlay';
        loadingDiv.style.position = 'absolute';
        loadingDiv.style.top = '50%';
        loadingDiv.style.left = '50%';
        loadingDiv.style.transform = 'translate(-50%, -50%)';
        loadingDiv.style.background = 'rgba(0,0,0,0.85)';
        loadingDiv.style.padding = '2rem';
        loadingDiv.style.borderRadius = '20px';
        loadingDiv.style.border = '2px solid #a855f7';
        loadingDiv.style.color = '#fff';
        loadingDiv.style.fontSize = '1.3rem';
        loadingDiv.style.textAlign = 'center';
        loadingDiv.style.zIndex = '9999';
        loadingDiv.innerHTML = '<div class="breath-circle inhale" style="width:45px; height:45px; margin: 0 auto 1rem auto; position:relative;"></div><p>Canalizando tu energía...<br><span style="font-size:0.95rem; color:#aaa;">Generando reporte personalizado en PDF.</span></p>';
        document.body.appendChild(loadingDiv);

        payload.image_b64 = canvasElement.toDataURL("image/jpeg", 0.9);
        if (capturedImage) capturedImage.src = payload.image_b64;

        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).then(r => r.json()).then(data => {
            const overlay = document.getElementById('aiLoadingOverlay');
            if(overlay) overlay.remove();
            
            if (data.success) callback(data);
            else { alert('Error del servidor: ' + (data.error || '')); resetToMenu(); }
        }).catch(err => {
            const overlay = document.getElementById('aiLoadingOverlay');
            if(overlay) overlay.remove();
            console.error(err); alert("Error de red local."); resetToMenu();
        });
    }

    // RESULTADOS AURA
    function showAuraResults(data) {
        resultsContainer.classList.remove('hidden');
        const userName = document.getElementById('userName').value.trim();
        resultsTitle.innerText = `Campo Áurico de ${userName || 'Consultante'}`;
        biorhythmPhrase.classList.add('hidden');
        analysisText.innerText = data.analysis;
        renderProducts(data.recommended_products, data.phone_target, data.pdf_filename);
    }

    // RESULTADOS BIORRITMO (REQUERIMIENTO 9: TARJETAS DE COLORES POR NIVEL EN PANTALLA)
    function showBiorhythmResults(data) {
        drawBiorhythmRings(data);
        capturedImage.src = canvasElement.toDataURL("image/jpeg", 0.9);
        
        resultsContainer.classList.remove('hidden');
        const userName = document.getElementById('userName').value.trim();
        resultsTitle.innerText = `Biorritmo Vital de ${userName || 'Consultante'}`;
        
        biorhythmPhrase.innerText = `"${data.frase || 'Tus cuatro cuerpos están en flujo vibracional.'}"`;
        biorhythmPhrase.classList.remove('hidden');
        
        // Renderizado estilizado de las tarjetas energéticas con sus porcentajes y colores
        analysisText.innerHTML = `
            <div class="biorhythm-summary-box">
                <h4 style="margin-bottom: 0.8rem; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 0.5rem; color: #a78bfa;">Niveles Energéticos Registrados</h4>
                <div class="biorhythm-bars-grid">
                    <div class="biorhythm-pill" style="border-left: 5px solid #ef4444; background: rgba(239, 68, 68, 0.15);">
                        <span style="color: #ef4444; font-weight: bold;">Físico</span>
                        <span class="bio-val" style="color: #ef4444;">${data.fisico}%</span>
                    </div>
                    <div class="biorhythm-pill" style="border-left: 5px solid #34d399; background: rgba(52, 211, 153, 0.15);">
                        <span style="color: #34d399; font-weight: bold;">Emocional</span>
                        <span class="bio-val" style="color: #34d399;">${data.emocional}%</span>
                    </div>
                    <div class="biorhythm-pill" style="border-left: 5px solid #fef08a; background: rgba(254, 240, 138, 0.15);">
                        <span style="color: #fef08a; font-weight: bold;">Intelectual</span>
                        <span class="bio-val" style="color: #fef08a;">${data.intelectual}%</span>
                    </div>
                    <div class="biorhythm-pill" style="border-left: 5px solid #a855f7; background: rgba(168, 85, 247, 0.15);">
                        <span style="color: #a855f7; font-weight: bold;">Espiritual</span>
                        <span class="bio-val" style="color: #a855f7;">${data.espiritual}%</span>
                    </div>
                </div>
            </div>
        `;
        
        renderProducts(data.recommended_products, data.phone_target, data.pdf_filename);
    }

    function drawBiorhythmRings(data) {
        canvasCtx.fillStyle = '#000000';
        canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);

        function drawLayer(radius, percent, color) {
            const expandedMask = createExpandedMask(staticMask, radius);
            
            const lCanvas = document.createElement('canvas');
            lCanvas.width = canvasElement.width; lCanvas.height = canvasElement.height;
            const lCtx = lCanvas.getContext('2d');
            
            lCtx.drawImage(expandedMask, 0, 0);
            lCtx.globalCompositeOperation = 'source-in';
            lCtx.fillStyle = 'rgba(0,0,0,0.85)';
            lCtx.fillRect(0, 0, lCanvas.width, lCanvas.height);
            
            const fillCanvas = document.createElement('canvas');
            fillCanvas.width = canvasElement.width; fillCanvas.height = canvasElement.height;
            const fCtx = fillCanvas.getContext('2d');
            
            fCtx.drawImage(expandedMask, 0, 0);
            fCtx.globalCompositeOperation = 'source-in';
            fCtx.fillStyle = color;
            fCtx.fillRect(0, 0, fillCanvas.width, fillCanvas.height);
            
            const emptyHeight = fillCanvas.height * (1 - (percent / 100));
            fCtx.globalCompositeOperation = 'destination-out';
            fCtx.fillRect(0, 0, fillCanvas.width, emptyHeight);

            const outlineCanvas = document.createElement('canvas');
            outlineCanvas.width = canvasElement.width; outlineCanvas.height = canvasElement.height;
            const oCtx = outlineCanvas.getContext('2d');
            
            oCtx.filter = `drop-shadow(0px 0px 4px ${color}) drop-shadow(0px 0px 8px ${color})`;
            oCtx.drawImage(expandedMask, 0, 0);
            oCtx.filter = 'none';
            oCtx.globalCompositeOperation = 'destination-out';
            oCtx.drawImage(expandedMask, 0, 0);

            lCtx.globalCompositeOperation = 'source-over';
            lCtx.drawImage(fillCanvas, 0, 0);
            lCtx.drawImage(outlineCanvas, 0, 0);

            canvasCtx.globalCompositeOperation = 'source-over';
            canvasCtx.drawImage(lCanvas, 0, 0);
        }

        drawLayer(140, data.espiritual, '#a855f7');
        drawLayer(95, data.intelectual, '#fef08a');
        drawLayer(55, data.emocional, '#34d399');
        drawLayer(20, data.fisico, '#ef4444');

        canvasCtx.globalCompositeOperation = 'source-over';
        canvasCtx.shadowBlur = 15;
        canvasCtx.shadowColor = 'rgba(0,0,0,1)';
        canvasCtx.drawImage(staticPerson, 0, 0);
        canvasCtx.shadowBlur = 0;
    }

    // REQUERIMIENTO 6 Y 8: RENDERIZADO DE PRODUCTO Y QR DE WHATSAPP COMPATIBLE OFFLINE Y WHATSAPP BUSINESS
    function renderProducts(products, phone, pdfFilename) {
        productsGrid.innerHTML = '';
        products.forEach(p => {
            productsGrid.innerHTML += `
                <div class="product-card">
                    <img src="${p.image}" alt="${p.name}">
                    <div>
                        <h4>${p.name}</h4>
                        <span>${p.type}</span>
                    </div>
                </div>
            `;
        });
        
        // Número de destino de WhatsApp del QR (Trememote: 5491123383837)
        const destPhone = "5491123383837";
        const msgText = `Hola estoy en la expo y quiero mi reporte ${pdfFilename}`;
        const waLink = `https://api.whatsapp.com/send?phone=${destPhone}&text=${encodeURIComponent(msgText)}`;
        
        // Generación de QR offline local si qrcode.js está disponible
        if (typeof QRCode !== 'undefined') {
            try {
                const qrGenerator = QRCode(6);
                waQrCode.src = qrGenerator.generateDataUrl(waLink, 200);
            } catch (e) {
                console.warn("Fallback a QR server si falla librería local", e);
                waQrCode.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(waLink)}`;
            }
        } else {
            waQrCode.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(waLink)}`;
        }
    }

    function resetToMenu() {
        if (currentStream && isCameraRunning) {
            currentStream.getTracks().forEach(t => t.stop());
            currentStream = null;
        }
        if (animFrameId) {
            cancelAnimationFrame(animFrameId);
            animFrameId = null;
        }
        isCameraRunning = false;
        isScanning = false;
        isFrozen = false;
        currentMode = null;
        
        resizeCanvas();
        
        mainMenuContainer.classList.remove('hidden');
        resultsContainer.classList.add('hidden');
        breathingUI.classList.add('hidden');
        biorhythmForm.classList.add('hidden');
    }

    resetBtn.addEventListener('click', resetToMenu);
});
