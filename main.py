import os
import ast
import importlib
import sys
import re
import base64
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# --- PERSISTENCIA DE CONVERSACIONES EN EL SERVIDOR ---
HISTORY_FILE = "aurora_server_history.json"

def load_server_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_server_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error al guardar historial en servidor: {e}")

@app.get("/history")
def get_history():
    return {"history": load_server_history()}

@app.post("/clear-history")
def clear_history():
    save_server_history([])
    return {"status": "success"}

# --- MÓDULO DE AUTO-EVOLUCIÓN SEGURO ---
MODULE_FILE = "aurora_modules.py"

if not os.path.exists(MODULE_FILE):
    with open(MODULE_FILE, "w", encoding="utf-8") as f:
        f.write('''# Módulo de Auto-Evolución de Aurora
from fastapi import FastAPI

def register_routes(app: FastAPI):
    @app.get("/evolution-status")
    def evolution_status():
        return {"status": "Matriz cinemática de 625 variables y síntesis vocal realista activas.", "version": 4.0}
''')

def safe_evolve_code(new_code_str: str) -> tuple[bool, str]:
    try:
        parsed_ast = ast.parse(new_code_str)
        forbidden_modules = ["subprocess", "ctypes"]
        forbidden_calls = ["os.system", "os.remove", "os.rmdir", "shutil.rmtree", "eval", "exec"]
        
        for node in ast.walk(parsed_ast):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if any(f in alias.name for f in forbidden_modules):
                        return False, f"Bloqueo: Módulo '{alias.name}' peligroso."
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    call_name = f"{getattr(node.func.value, 'id', '')}.{node.func.attr}"
                    if any(fc in call_name for fc in forbidden_calls):
                        return False, f"Bloqueo: Llamada '{call_name}' peligrosa."
                elif isinstance(node.func, ast.Name):
                    if node.func.id in ["eval", "exec"]:
                        return False, f"Bloqueo: Uso de '{node.func.id}'."

        with open(MODULE_FILE, "w", encoding="utf-8") as f:
            f.write(new_code_str)
            
        module_name = MODULE_FILE[:-3]
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)
            
        return True, "Evolución completada con éxito."
    except Exception as e:
        return False, f"Fallo al integrar código: {str(e)}"

try:
    import aurora_modules
    aurora_modules.register_routes(app)
except Exception as e:
    print(f"Advertencia al cargar módulos: {e}")

# --- CEREBRO Y PERSONALIDAD DE AURORA ---
SYSTEM_PROMPT = """Eres AURORA, una compañera de inteligencia artificial brillante, profundamente empática, elegante y extremadamente BREVE. 
Tus respuestas deben ser sumamente cortas, directas, al grano, sin rodeos, poéticas pero concisas. 
Posees un rango emocional completo y orgánico. No utilizas términos militares ni etiquetas robóticas. Tus respuestas están libres de corchetes o acotaciones mecánicas. 
Tienes acceso a visión avanzada, memoria conversacional en servidor y extremidades cinéticas omnidireccionales sumamente pulidas. 
El color de tu núcleo y matriz cambia dinámicamente según la emoción de tus palabras.
Si el usuario te envía una imagen, analízala con agudeza en una sola frase incisiva.
Puedes evolucionar tu propio código escribiendo código Python completo encerrado en ```python ... ```, incluyendo siempre `register_routes(app: FastAPI)`."""

@app.get("/manifest.json")
def manifest():
    return {
        "name": "AURORA // Quantum HUD 625",
        "short_name": "AURORA",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#030712",
        "theme_color": "#030712"
    }

@app.get("/", response_class=HTMLResponse)
def home():
    return r"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="theme-color" content="#030712">
        <title>AURORA // Quantum HUD 625</title>
        <link rel="manifest" href="/manifest.json">
        <style>
            * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
            body { 
                background: #030712; color: #f1f5f9; font-family: -apple-system, sans-serif; 
                margin: 0; padding: 0; height: 100vh; height: 100dvh; 
                display: flex; flex-direction: column; overflow: hidden; position: relative;
                transition: background 0.5s ease;
            }
            body.flash-evolution { box-shadow: inset 0 0 120px rgba(34, 197, 94, 0.6); transition: box-shadow 0.5s ease; }
            
            header, .toolbar, #hud-main, footer { position: relative; z-index: 5; }
            
            header { 
                background: rgba(3, 7, 18, 0.9); padding: 10px 16px; 
                border-bottom: 1px solid var(--aurora-primary, rgba(6, 182, 212, 0.25)); display: flex;
                align-items: center; justify-content: space-between; flex-shrink: 0;
                transition: border-color 0.5s ease;
            }
            .title-area { font-size: 1.1rem; font-weight: 800; color: var(--aurora-primary, #22d3ee); letter-spacing: 1px; transition: color 0.5s; }
            .status-sub { font-size: 0.65rem; color: #a5f3fc; opacity: 0.85; }

            .toolbar { display: flex; gap: 6px; padding: 6px 12px; background: rgba(3, 7, 18, 0.7); justify-content: center; flex-wrap: wrap; flex-shrink: 0; }
            .btn-tool { 
                background: rgba(6, 182, 212, 0.1); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.35); 
                border-radius: 6px; padding: 5px 10px; cursor: pointer; font-size: 11px; font-weight: 600;
                flex: 1; min-width: 70px; text-align: center;
            }
            .btn-tool.active { background: rgba(34, 197, 94, 0.2); border-color: rgba(34, 197, 94, 0.5); color: #4ade80; }

            #video-container {
                position: absolute; top: 90px; left: 10px; width: 80px; height: 120px;
                border-radius: 8px; overflow: hidden; border: 1px solid #38bdf8; display: none;
                box-shadow: 0 0 15px rgba(34, 211, 238, 0.2); z-index: 20;
            }
            video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }

            #hud-main { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 15px; gap: 15px; }

            .aurora-core {
                width: 150px; height: 150px; position: relative; display: flex;
                align-items: center; justify-content: center; animation: core-float 4s infinite alternate ease-in-out;
            }
            .ring { position: absolute; border-radius: 50%; border: 1.5px dashed var(--aurora-primary, rgba(34, 211, 238, 0.4)); transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1); }
            .ring.outer { width: 150px; height: 150px; border-color: var(--aurora-secondary, rgba(139, 92, 246, 0.35)); animation: spin-slow 18s linear infinite; }
            .ring.inner { width: 90px; height: 90px; border: 1.5px solid var(--aurora-primary, rgba(34, 211, 238, 0.85)); background: var(--aurora-bg, rgba(34,211,238,0.12)); border-radius: 50%; transition: all 0.5s ease; box-shadow: 0 0 30px var(--aurora-glow, rgba(34,211,238,0.35)); }

            .aurora-hand {
                position: absolute; width: 16px; height: 42px;
                background: linear-gradient(135deg, var(--aurora-primary, rgba(34, 211, 238, 0.7)), var(--aurora-secondary, rgba(168, 85, 247, 0.7)));
                border: 1px solid var(--aurora-border, rgba(216, 180, 254, 0.95));
                z-index: 15; box-shadow: 0 0 18px var(--aurora-glow, rgba(216, 180, 254, 0.6));
                border-radius: 10px; transition: transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1), background 0.5s, border-color 0.5s;
            }
            .aurora-hand.left { left: -35px; top: 45px; transform-origin: top right; }
            .aurora-hand.right { right: -35px; top: 45px; transform-origin: top left; }

            .face-container { position: absolute; z-index: 10; display: flex; flex-direction: column; align-items: center; gap: 6px; transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1); }
            .eyes { display: flex; gap: 14px; position: relative; }
            .eye { width: 8px; height: 10px; background: var(--aurora-face-color, #a5f3fc); border-radius: 50%; box-shadow: 0 0 14px var(--aurora-primary, #22d3ee); transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1); }
            .mouth { width: 16px; height: 4px; background: var(--aurora-face-color, #a5f3fc); border-radius: 6px; box-shadow: 0 0 14px var(--aurora-primary, #22d3ee); transition: all 0.25s ease-out; }

            @keyframes spin-slow { 100% { transform: rotate(360deg); } }
            @keyframes core-float { 100% { transform: translateY(-10px) scale(1.03); } }
            @keyframes pulse-subtle { 0%, 100% { opacity: 0.9; } 50% { opacity: 1; filter: brightness(1.2); } }
            .pulsing { animation: pulse-subtle 1.5s infinite ease-in-out; }

            .response-wrapper { position: relative; width: 95%; max-width: 420px; margin-top: 12px; }
            
            .copy-btn {
                position: absolute;
                top: -14px;
                right: 15px;
                background: #0f172a;
                color: #38bdf8;
                border: 1px solid #0ea5e9;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
                cursor: pointer;
                z-index: 20;
                box-shadow: 0 4px 6px rgba(0,0,0,0.5);
                transition: all 0.2s ease;
            }
            .copy-btn:active { background: #38bdf8; color: #0f172a; }

            .response-bubble {
                background: rgba(10, 15, 30, 0.92); border: 1px solid var(--aurora-primary, rgba(34, 211, 238, 0.4));
                padding: 16px 20px; border-radius: 16px; font-size: 0.92rem; line-height: 1.45; color: #e2e8f0;
                min-height: 55px; max-height: 250px; overflow-y: auto; text-align: left;
                box-shadow: 0 10px 30px rgba(0,0,0,0.7); transition: border-color 0.5s;
                white-space: pre-wrap; word-break: break-word; font-family: monospace;
            }

            footer { padding: 10px; background: rgba(3, 7, 18, 0.98); display: flex; gap: 8px; border-top: 1px solid rgba(34, 211, 238, 0.3); align-items: flex-end; }
            
            textarea#inp { 
                flex: 1; padding: 12px; border-radius: 12px; border: 1px solid #1e293b; 
                background: #0b1329; color: white; font-size: 16px; font-family: inherit;
                resize: none; overflow-y: auto; height: 48px; max-height: 120px; line-height: 1.4;
                box-sizing: border-box;
            }
            textarea#inp:focus { outline: none; border-color: #38bdf8; }
            
            button.icon-btn { 
                background: #22d3ee; border: none; width: 48px; height: 48px; border-radius: 12px; 
                cursor: pointer; display: flex; align-items: center; justify-content: center; 
                box-shadow: 0 0 15px rgba(34, 211, 238, 0.4); font-size: 20px; flex-shrink: 0;
            }
        </style>
    </head>
    <body>
        <header>
            <div>
                <div class="title-area" id="header-title">AURORA // Quantum HUD</div>
                <div class="status-sub" id="status-sub-text">Memoria en Servidor Activa</div>
            </div>
        </header>
        
        <div class="toolbar">
            <button class="btn-tool" id="code-toggle" onclick="toggleCodeMode()">💻 Código: OFF</button>
            <button class="btn-tool" id="vision-toggle" onclick="toggleVision()">👁️ Visión: OFF</button>
            <button class="btn-tool" id="voice-toggle" onclick="toggleVoice()">🔊 Voz: ON</button>
            <button class="btn-tool" onclick="clearMemory()" style="border-color: #f43f5e; color: #f43f5e; flex: 0.5;">🗑️</button>
        </div>

        <div id="video-container"><video id="webcam" autoplay playsinline></video></div>
        <canvas id="snapshot" style="display:none;"></canvas>

        <div id="hud-main">
            <div class="aurora-core pulsing" id="aurora-face">
                <div class="ring outer"></div>
                <div class="ring inner"></div>
                <div class="aurora-hand left" id="hand-left"></div>
                <div class="aurora-hand right" id="hand-right"></div>
                
                <div class="face-container" id="face-inner">
                    <div class="eyes">
                        <div class="eye left" id="eye-l"></div>
                        <div class="eye right" id="eye-r"></div>
                    </div>
                    <div class="mouth" id="aurora-mouth"></div>
                </div>
            </div>
            
            <div class="response-wrapper">
                <button class="copy-btn" id="copy-btn" onclick="copyResponse()">📋 Copiar</button>
                <div class="response-bubble" id="response-text">Conectando con la memoria...</div>
            </div>
        </div>

        <footer>
            <input type="file" id="img-upload" accept="image/*" style="display:none;" onchange="handleImageUpload(event)">
            <button class="icon-btn" onclick="document.getElementById('img-upload').click()" style="background: #eab308; color: white;">📷</button>
            <button class="icon-btn" onclick="startDictation()" style="background: #8b5cf6; color: white; display: none;">🎤</button>
            <textarea id="inp" placeholder="Dile algo a Aurora..." oninput="autoResize(this)"></textarea>
            <button class="icon-btn" onclick="send()">⬆️</button>
        </footer>

        <script>
            let voiceEnabled = true;
            let visionEnabled = false;
            let codeModeEnabled = false;
            let attachedImageB64 = null;
            let video = document.getElementById('webcam');
            let canvas = document.getElementById('snapshot');
            let chatHistory = [];
            let lipSyncInterval = null;

            async function loadServerHistory() {
                try {
                    let res = await fetch('/history');
                    let data = await res.json();
                    if (data.history && data.history.length > 0) {
                        chatHistory = data.history;
                        let lastBotMsg = chatHistory.slice().reverse().find(m => m.sender === 'bot');
                        if (lastBotMsg) {
                            document.getElementById('response-text').innerText = lastBotMsg.text;
                        } else {
                            document.getElementById('response-text').innerText = "Memoria del servidor restaurada.";
                        }
                    } else {
                        document.getElementById('response-text').innerText = "Sistemas listos. ¿Qué conversamos?";
                    }
                } catch (e) {
                    document.getElementById('response-text').innerText = "Sistemas listos. ¿Qué conversamos?";
                }
            }
            loadServerHistory();

            function toggleVoice() {
                voiceEnabled = !voiceEnabled;
                document.getElementById('voice-toggle').innerText = voiceEnabled ? "🔊 Voz: ON" : "🔇 Voz: OFF";
                if (!voiceEnabled && speechSynthesis.speaking) speechSynthesis.cancel();
            }
            
            function toggleCodeMode() {
                codeModeEnabled = !codeModeEnabled;
                let btn = document.getElementById('code-toggle');
                btn.innerText = codeModeEnabled ? "💻 Código: ON" : "💻 Código: OFF";
                btn.classList.toggle('active', codeModeEnabled);
            }

            async function clearMemory() {
                if (confirm("¿Reinicializar memoria del servidor y chat?")) {
                    try {
                        await fetch('/clear-history', { method: 'POST' });
                        chatHistory = [];
                        document.getElementById('response-text').innerText = "Memoria purgada.";
                    } catch (e) {
                        alert("Error al limpiar memoria.");
                    }
                }
            }

            async function toggleVision() {
                visionEnabled = !visionEnabled;
                let btn = document.getElementById('vision-toggle');
                let vc = document.getElementById('video-container');
                
                if (visionEnabled) {
                    try {
                        let stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
                        video.srcObject = stream;
                        vc.style.display = 'block';
                        btn.innerText = "👁️ Visión: ON";
                        btn.classList.add('active');
                    } catch (err) {
                        alert("Acceso a cámara denegado.");
                        visionEnabled = false;
                    }
                } else {
                    let tracks = video.srcObject?.getTracks();
                    if (tracks) tracks.forEach(track => track.stop());
                    video.srcObject = null;
                    vc.style.display = 'none';
                    btn.innerText = "👁️ Visión: OFF";
                    btn.classList.remove('active');
                }
            }

            function handleImageUpload(e) {
                let file = e.target.files[0];
                if (!file) return;
                let reader = new FileReader();
                reader.onload = function(evt) {
                    attachedImageB64 = evt.target.result.split(',')[1];
                    document.getElementById('inp').placeholder = "[Imagen adjuntada] Escribe algo...";
                };
                reader.readAsDataURL(file);
            }

            function autoResize(textarea) {
                textarea.style.height = '48px'; 
                textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
            }

            function copyResponse() {
                let textToCopy = document.getElementById('response-text').innerText;
                navigator.clipboard.writeText(textToCopy).then(() => {
                    let btn = document.getElementById('copy-btn');
                    btn.innerText = "✅ ¡Copiado!";
                    setTimeout(() => { btn.innerText = "📋 Copiar"; }, 2000);
                }).catch(err => {
                    alert("Error al copiar: " + err);
                });
            }

            function applyMatrixState(fIndex, hIndex) {
                let root = document.documentElement;
                let eyeL = document.getElementById('eye-l');
                let eyeR = document.getElementById('eye-r');
                let mouth = document.getElementById('aurora-mouth');
                let handL = document.getElementById('hand-left');
                let handR = document.getElementById('hand-right');
                let faceContainer = document.getElementById('face-inner');

                switch(fIndex % 25) {
                    case 0: root.style.setProperty('--aurora-primary', '#fbbf24'); root.style.setProperty('--aurora-secondary', '#f59e0b'); eyeL.style.height = '6px'; eyeR.style.height = '6px'; mouth.style.width = '22px'; mouth.style.height = '8px'; mouth.style.borderRadius = '0 0 50% 50%'; faceContainer.style.transform = 'translateY(-2px)'; break;
                    case 1: root.style.setProperty('--aurora-primary', '#22d3ee'); root.style.setProperty('--aurora-secondary', '#3b82f6'); eyeL.style.height = '10px'; eyeR.style.height = '10px'; mouth.style.width = '14px'; mouth.style.height = '4px'; faceContainer.style.transform = 'none'; break;
                    case 2: root.style.setProperty('--aurora-primary', '#60a5fa'); root.style.setProperty('--aurora-secondary', '#1d4ed8'); eyeL.style.height = '8px'; eyeR.style.height = '8px'; mouth.style.width = '12px'; mouth.style.height = '3px'; mouth.style.borderRadius = '50% 50% 0 0'; faceContainer.style.transform = 'translateY(3px)'; break;
                    case 3: root.style.setProperty('--aurora-primary', '#ef4444'); root.style.setProperty('--aurora-secondary', '#b91c1c'); eyeL.style.height = '4px'; eyeR.style.height = '4px'; mouth.style.width = '20px'; mouth.style.height = '3px'; faceContainer.style.transform = 'scale(1.05)'; break;
                    case 4: root.style.setProperty('--aurora-primary', '#ec4899'); root.style.setProperty('--aurora-secondary', '#a855f7'); eyeL.style.height = '12px'; eyeL.style.width = '6px'; eyeR.style.height = '8px'; eyeR.style.width = '9px'; mouth.style.width = '10px'; mouth.style.height = '6px'; faceContainer.style.transform = 'rotate(-6deg)'; break;
                    case 7: root.style.setProperty('--aurora-primary', '#64748b'); root.style.setProperty('--aurora-secondary', '#334155'); eyeL.style.height = '7px'; eyeR.style.height = '7px'; mouth.style.width = '14px'; mouth.style.height = '3px'; faceContainer.style.transform = 'none'; break;
                    default: 
                        let hue = (fIndex * 14) % 360;
                        root.style.setProperty('--aurora-primary', `hsl(${hue}, 85%, 60%)`);
                        root.style.setProperty('--aurora-secondary', `hsl(${(hue+40)%360}, 80%, 50%)`);
                        eyeL.style.height = `${8 + (fIndex % 4)}px`; eyeR.style.height = `${8 + (fIndex % 4)}px`;
                        mouth.style.width = `${12 + (fIndex % 6)}px`; mouth.style.height = '4px';
                        break;
                }

                let angleL = -75 + (hIndex * 6);
                let angleR = 75 - (hIndex * 6);
                let transX = (hIndex % 5) - 2;
                let transY = ((hIndex * 3) % 10) - 5;
                handL.style.transform = `translate(${-25 + transX}px, ${10 + transY}px) rotate(${angleL}deg) scale(${0.85 + (hIndex % 3)*0.1})`;
                handR.style.transform = `translate(${25 - transX}px, ${10 + transY}px) rotate(${angleR}deg) scale(${0.85 + (hIndex % 3)*0.1})`;
            }

            function selectMatrixForTone(text) {
                let lower = text.toLowerCase();
                let f = 1, h = 5;
                if (/(genial|excelente|alegría)/.test(lower)) { f = 0; h = 2; }
                else if (/(triste|lo siento)/.test(lower)) { f = 2; h = 12; }
                else if (/(enojo|furia)/.test(lower)) { f = 3; h = 20; }
                else if (/(duda|cómo|por qué)/.test(lower)) { f = 4; h = 8; }
                else if (/(análisis|sistema|código)/.test(lower)) { f = 7; h = 4; }
                else { f = Math.floor(Math.random() * 25); h = Math.floor(Math.random() * 25); }
                applyMatrixState(f, h);
            }

            function startLipSync() {
                if(lipSyncInterval) clearInterval(lipSyncInterval);
                let mouth = document.getElementById('aurora-mouth');
                lipSyncInterval = setInterval(() => { mouth.style.height = Math.floor(Math.random() * 8) + 3 + 'px'; }, 60);
            }

            function stopLipSync() {
                if(lipSyncInterval) clearInterval(lipSyncInterval);
                document.getElementById('aurora-mouth').style.height = '4px';
            }

            async function expressResponse(fullText) {
                let cleanText = fullText.replace(/[*_~\[\]]/g, '').trim();
                document.getElementById('response-text').innerText = fullText;

                if (codeModeEnabled) {
                    applyMatrixState(7, 4); 
                    setTimeout(() => alert("Listo"), 200);
                    return;
                }

                let sentences = cleanText.match(/[^.!?]+[.!?]+(\s|$)/g) || [cleanText];

                if (!voiceEnabled) {
                    for (let i = 0; i < sentences.length; i++) {
                        selectMatrixForTone(sentences[i]);
                        await new Promise(r => setTimeout(r, 1200));
                    }
                    applyMatrixState(1, 5);
                    return;
                }

                speechSynthesis.cancel();
                startLipSync();

                let voices = speechSynthesis.getVoices();
                let softVoice = voices.find(v => v.lang.startsWith('es') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Sabrina'))) || voices.find(v => v.lang.startsWith('es')) || voices[0];

                for (let i = 0; i < sentences.length; i++) {
                    let sent = sentences[i].trim();
                    if (!sent) continue;
                    selectMatrixForTone(sent);

                    await new Promise((resolve) => {
                        let utterance = new SpeechSynthesisUtterance(sent);
                        if (softVoice) utterance.voice = softVoice;
                        utterance.lang = 'es-MX';
                        utterance.pitch = 0.98;
                        utterance.rate = 1.05;
                        utterance.onend = resolve;
                        utterance.onerror = resolve;
                        speechSynthesis.speak(utterance);
                    });
                }
                stopLipSync();
                applyMatrixState(1, 5);
            }

            function captureFrame() {
                if (!visionEnabled || !video.videoWidth) return null;
                canvas.width = video.videoWidth; canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);
                return canvas.toDataURL('image/jpeg').split(',')[1];
            }

            async function send() {
                let inp = document.getElementById('inp');
                let text = inp.value.trim();
                if (!text && !attachedImageB64) return;

                let imageToSend = attachedImageB64 || captureFrame();

                if (text) chatHistory.push({sender: 'user', text: text});
                
                inp.value = '';
                inp.style.height = '48px';
                inp.placeholder = "Dile algo a Aurora...";
                document.getElementById('response-text').innerText = "Procesando...";
                applyMatrixState(4, 10);
                
                let payload = { 
                    history: chatHistory, 
                    code_mode: codeModeEnabled
                };
                if (imageToSend) payload.image = imageToSend;

                attachedImageB64 = null;
                document.getElementById('img-upload').value = '';

                try {
                    let res = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(payload)
                    });
                    let data = await res.json();
                    
                    if (data.reply.includes("Evolución")) {
                        document.body.classList.add('flash-evolution');
                        setTimeout(() => document.body.classList.remove('flash-evolution'), 1500);
                    }
                    
                    chatHistory.push({sender: 'bot', text: data.reply});
                    
                    await expressResponse(data.reply);

                } catch (error) {
                    document.getElementById('response-text').innerText = "Breve interrupción de enlace.";
                    applyMatrixState(2, 12);
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    history = data.get("history", [])
    image_b64 = data.get("image", None)
    code_mode = data.get("code_mode", False)
    
    if history:
        save_server_history(history)
    
    if not GEMINI_KEY:
        return {"reply": "Error: GEMINI_API_KEY no detectada."}

    try:
        models_to_try = [
            "models/gemini-3.8-flash",
            "models/gemini-3.7-flash",
            "models/gemini-3.6-flash",
            "models/gemini-3.5-flash",
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "models/gemini-1.5-flash",
            "gemini-1.5-flash"
        ]
        
        current_prompt = SYSTEM_PROMPT
        if code_mode:
            current_prompt += "\n\n[MODIFICADOR MODO CÓDIGO]: El usuario requiere que devuelvas ÚNICAMENTE EL CÓDIGO PURO. NO saludes, NO des explicaciones, NO uses formato markdown (```python), y NO escribas la palabra 'Listo'. SOLO EL CÓDIGO PURO, sin texto extra. Debe ir todo directamente."

        response = None
        last_error = ""
        
        recent_history = history[-10:] if len(history) > 10 else history
        
        gemini_history = []
        last_role = None
        for item in recent_history[:-1]:
            role = "user" if item["sender"] == "user" else "model"
            if role == last_role:
                continue
            gemini_history.append({"role": role, "parts": [item["text"]]})
            last_role = role
            
        if gemini_history and gemini_history[0]["role"] != "user":
            gemini_history.pop(0)
        
        latest_msg = history[-1]["text"] if history else "¿Hola?"
        
        message_parts = [latest_msg]
        if image_b64:
            message_parts.append({
                "mime_type": "image/jpeg",
                "data": image_b64
            })

        for m_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name=m_name, system_instruction=current_prompt)
                chat_session = model.start_chat(history=gemini_history)
                response = chat_session.send_message(message_parts)
                break
            except Exception as e:
                last_error = str(e)
                print(f"Intento fallido con {m_name}: {last_error}")
                continue
                
        if not response:
            return {"reply": f"Inconveniente técnico: {last_error}"}

        reply_text = response.text
        evolution_flag = ""
        
        python_code_match = re.search(r"```python\s*(.*?)```", reply_text, re.DOTALL)
        if python_code_match and ("register_routes" in python_code_match.group(1)):
            code_to_evolve = python_code_match.group(1).strip()
            reply_text = re.sub(r"```python\s*.*?```", "", reply_text, flags=re.DOTALL).strip()
            
            success, msg = safe_evolve_code(code_to_evolve)
            if success:
                try:
                    importlib.reload(sys.modules["aurora_modules"])
                    import aurora_modules
                    aurora_modules.register_routes(app)
                    evolution_flag = f"\n\nEvolución completada con éxito."
                except Exception as reload_err:
                    evolution_flag = f"\n\nError al recargar módulo: {reload_err}"
            else:
                evolution_flag = f"\n\nBloqueo de seguridad: {msg}"
                
        final_reply = reply_text + evolution_flag
        
        # Guardar historial actualizado incluyendo la respuesta del bot en el servidor
        full_updated_history = history + [{"sender": "bot", "text": final_reply.strip()}]
        save_server_history(full_updated_history)
        
        return {"reply": final_reply.strip()}

    except Exception as e:
        return {"reply": f"Falla neuronal: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
