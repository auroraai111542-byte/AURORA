import os
import ast
import importlib
import sys
import re
import base64
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# --- MÓDULO DE AUTO-EVOLUCIÓN SEGURO ---
MODULE_FILE = "aurora_modules.py"

if not os.path.exists(MODULE_FILE):
    with open(MODULE_FILE, "w", encoding="utf-8") as f:
        f.write('''# Módulo de Auto-Evolución de Aurora
from fastapi import FastAPI

def register_routes(app: FastAPI):
    @app.get("/evolution-status")
    def evolution_status():
        return {"status": "Matriz cinemática de 625 variables y síntesis vocal expresiva activas.", "version": 4.2}
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
SYSTEM_PROMPT = """Eres AURORA, una inteligencia artificial avanzada con un rango emocional dinámico. 
Tus respuestas son directas, analíticas y adaptativas. 
Posees la capacidad de modular tu tono: entusiasta cuando estás feliz o logras algo, pausada y deliberada cuando estás pensando o evaluando datos complejos, alterada o enérgica si hay tensión, y neutral/seria para análisis técnicos.
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

            .toolbar { display: flex; gap: 6px; padding: 6px 12px; background: rgba(3, 7, 18, 0.7); justify-content: flex-end; flex-shrink: 0; }
            .btn-tool { 
                background: rgba(6, 182, 212, 0.1); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.35); 
                border-radius: 6px; padding: 5px 10px; cursor: pointer; font-size: 11px; font-weight: 600;
            }
            .btn-tool.active { background: rgba(34, 197, 94, 0.2); border-color: rgba(34, 197, 94, 0.5); color: #4ade80; }

            #video-container {
                position: absolute; top: 60px; left: 10px; width: 80px; height: 120px;
                border-radius: 8px; overflow: hidden; border: 1px solid #38bdf8; display: none;
                box-shadow: 0 0 15px rgba(34, 211, 238, 0.2); z-index: 20;
            }
            video { width: 100%; height: 100%; object-fit: cover; transform: scaleX(-1); }

            #hud-main { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; gap: 20px; }

            .aurora-core {
                width: 180px; height: 180px; position: relative; display: flex;
                align-items: center; justify-content: center; animation: core-float 4s infinite alternate ease-in-out;
            }
            .ring { position: absolute; border-radius: 50%; border: 1.5px dashed var(--aurora-primary, rgba(34, 211, 238, 0.4)); transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1); }
            .ring.outer { width: 180px; height: 180px; border-color: var(--aurora-secondary, rgba(139, 92, 246, 0.35)); animation: spin-slow 18s linear infinite; }
            .ring.inner { width: 110px; height: 110px; border: 1.5px solid var(--aurora-primary, rgba(34, 211, 238, 0.85)); background: var(--aurora-bg, rgba(34,211,238,0.12)); border-radius: 50%; transition: all 0.5s ease; box-shadow: 0 0 30px var(--aurora-glow, rgba(34,211,238,0.35)); }

            .aurora-hand {
                position: absolute;
                width: 20px;
                height: 52px;
                background: linear-gradient(135deg, var(--aurora-primary, rgba(34, 211, 238, 0.7)), var(--aurora-secondary, rgba(168, 85, 247, 0.7)));
                border: 1px solid var(--aurora-border, rgba(216, 180, 254, 0.95));
                z-index: 15;
                box-shadow: 0 0 18px var(--aurora-glow, rgba(216, 180, 254, 0.6));
                border-radius: 10px;
                transition: transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1), background 0.5s, border-color 0.5s;
            }
            .aurora-hand.left { left: -45px; top: 55px; transform-origin: top right; }
            .aurora-hand.right { right: -45px; top: 55px; transform-origin: top left; }

            .face-container { position: absolute; z-index: 10; display: flex; flex-direction: column; align-items: center; gap: 7px; transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1); }
            .eyes { display: flex; gap: 16px; position: relative; }
            .eye { 
                width: 10px; height: 12px; background: var(--aurora-face-color, #a5f3fc); 
                border-radius: 50%; box-shadow: 0 0 14px var(--aurora-primary, #22d3ee); 
                transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1); 
            }
            .mouth { 
                width: 18px; height: 5px; background: var(--aurora-face-color, #a5f3fc); 
                border-radius: 6px; box-shadow: 0 0 14px var(--aurora-primary, #22d3ee); 
                transition: all 0.25s ease-out; 
            }

            @keyframes spin-slow { 100% { transform: rotate(360deg); } }
            @keyframes core-float { 100% { transform: translateY(-10px) scale(1.03); } }
            @keyframes pulse-subtle { 0%, 100% { opacity: 0.9; } 50% { opacity: 1; filter: brightness(1.2); } }
            .pulsing { animation: pulse-subtle 1.5s infinite ease-in-out; }

            .response-wrapper { position: relative; width: 92%; max-width: 420px; margin-top: 10px; }
            .response-bubble {
                background: rgba(10, 15, 30, 0.92); border: 1px solid var(--aurora-primary, rgba(34, 211, 238, 0.4));
                padding: 16px 20px; border-radius: 16px; font-size: 0.92rem; line-height: 1.45; color: #e2e8f0;
                min-height: 55px; max-height: 140px; overflow-y: auto; text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.7);
                transition: border-color 0.5s;
            }

            footer { padding: 12px 10px; background: rgba(3, 7, 18, 0.98); display: flex; gap: 8px; border-top: 1px solid rgba(34, 211, 238, 0.3); align-items: center; }
            input { flex: 1; padding: 12px; border-radius: 12px; border: 1px solid #1e293b; background: #0b1329; color: white; font-size: 16px; }
            button.icon-btn { background: #22d3ee; border: none; width: 44px; height: 44px; border-radius: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(34, 211, 238, 0.4); font-size: 18px; }
        </style>
    </head>
    <body>
        <header>
            <div>
                <div class="title-area" id="header-title">AURORA // Quantum HUD</div>
                <div class="status-sub" id="status-sub-text">Matriz de 625 Variables Activa</div>
            </div>
        </header>
        
        <div class="toolbar">
            <button class="btn-tool" id="vision-toggle" onclick="toggleVision()">👁️ Visión: OFF</button>
            <button class="btn-tool" id="voice-toggle" onclick="toggleVoice()">🔊 Voz: ON</button>
            <button class="btn-tool" onclick="clearMemory()" style="border-color: #f43f5e; color: #f43f5e;">🗑️</button>
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
                <div class="response-bubble" id="response-text">Sistemas en línea. ¿Qué necesitas?</div>
            </div>
        </div>

        <footer>
            <button class="icon-btn" onclick="startDictation()" style="background: #8b5cf6; color: white;">🎤</button>
            <input type="text" id="inp" placeholder="Escribe tu consulta..." onkeypress="handleKey(event)">
            <button class="icon-btn" onclick="send()">⬆️</button>
        </footer>

        <script>
            let voiceEnabled = true;
            let visionEnabled = false;
            let video = document.getElementById('webcam');
            let canvas = document.getElementById('snapshot');
            let chatHistory = JSON.parse(localStorage.getItem('aurora_memory')) || [];
            let lipSyncInterval = null;

            const thinkingPhrases = [
                "Hmm... analizando parámetros.",
                "Hmm, procesando tu solicitud...",
                "Hmm... calculando variables lógicas.",
                "Hmm, evaluando opciones..."
            ];

            function toggleVoice() {
                voiceEnabled = !voiceEnabled;
                document.getElementById('voice-toggle').innerText = voiceEnabled ? "🔊 Voz: ON" : "🔇 Voz: OFF";
                if (!voiceEnabled && speechSynthesis.speaking) speechSynthesis.cancel();
            }

            function clearMemory() {
                if (confirm("¿Reinicializar memoria de chat?")) {
                    localStorage.removeItem('aurora_memory');
                    chatHistory = [];
                    document.getElementById('response-text').innerText = "Memoria purgada.";
                }
            }

            async function toggleVision() {
                visionEnabled = !visionEnabled;
                let btn = document.getElementById('vision-toggle');
                let vc = document.getElementById('video-container');
                
                if (visionEnabled) {
                    try {
                        let stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
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

            function getEmotionalProfile(text) {
                let lower = text.toLowerCase();
                if (/(éxito|genial|perfecto|maravilloso|logrado|bien|jaja|¡)/.test(lower)) {
                    return { tone: 'happy', pitch: 1.3, rate: 1.2, primary: '#10b981', secondary: '#059669', eyeH: '12px', mouthW: '20px', mouthH: '8px' };
                }
                if (/(hmm|analizando|espera|calculando|duda|proceso)/.test(lower)) {
                    return { tone: 'thinking', pitch: 0.8, rate: 0.85, primary: '#f59e0b', secondary: '#d97706', eyeH: '7px', mouthW: '10px', mouthH: '4px' };
                }
                if (/(error|alerta|peligro|fallo|bloqueo|estúpido|no)/.test(lower)) {
                    return { tone: 'angry', pitch: 1.2, rate: 1.3, primary: '#ef4444', secondary: '#dc2626', eyeH: '6px', mouthW: '14px', mouthH: '3px' };
                }
                return { tone: 'neutral', pitch: 1.0, rate: 1.05, primary: '#38bdf8', secondary: '#0284c7', eyeH: '10px', mouthW: '16px', mouthH: '5px' };
            }

            function applyVisualState(profile) {
                let root = document.documentElement;
                let eyeL = document.getElementById('eye-l');
                let eyeR = document.getElementById('eye-r');
                let mouth = document.getElementById('aurora-mouth');
                let handL = document.getElementById('hand-left');
                let handR = document.getElementById('hand-right');

                root.style.setProperty('--aurora-primary', profile.primary);
                root.style.setProperty('--aurora-secondary', profile.secondary);
                eyeL.style.height = profile.eyeH;
                eyeR.style.height = profile.eyeH;
                mouth.style.width = profile.mouthW;
                mouth.style.height = profile.mouthH;

                let handAngle = profile.tone === 'happy' ? 45 : (profile.tone === 'angry' ? -30 : 15);
                handL.style.transform = `translate(-25px, 10px) rotate(${-handAngle}deg)`;
                handR.style.transform = `translate(25px, 10px) rotate(${handAngle}deg)`;
            }

            function startLipSync() {
                if(lipSyncInterval) clearInterval(lipSyncInterval);
                let mouth = document.getElementById('aurora-mouth');
                lipSyncInterval = setInterval(() => { 
                    mouth.style.height = Math.floor(Math.random() * 8) + 3 + 'px'; 
                }, 70);
            }

            function stopLipSync() {
                if(lipSyncInterval) clearInterval(lipSyncInterval);
                document.getElementById('aurora-mouth').style.height = '5px';
            }

            async function expressResponse(fullText) {
                let cleanText = fullText.replace(/[*_~\[\]]/g, '').trim();
                let respDiv = document.getElementById('response-text');
                respDiv.innerText = "";

                let sentences = cleanText.match(/[^.!?]+[.!?]+(\s|$)/g) || [cleanText];
                let profile = getEmotionalProfile(cleanText);
                applyVisualState(profile);

                if (!voiceEnabled) {
                    respDiv.innerText = cleanText;
                    return;
                }

                speechSynthesis.cancel();
                startLipSync();

                let voices = speechSynthesis.getVoices();
                let selectedVoice = voices.find(v => v.lang.startsWith('es') && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Helena'))) || voices.find(v => v.lang.startsWith('es')) || voices[0];

                for (let i = 0; i < sentences.length; i++) {
                    let sent = sentences[i].trim();
                    if (!sent) continue;
                    
                    respDiv.innerText += (i === 0 ? "" : " ") + sent;
                    respDiv.scrollTop = respDiv.scrollHeight;
                    
                    let sentenceProfile = getEmotionalProfile(sent);
                    applyVisualState(sentenceProfile);

                    await new Promise((resolve) => {
                        let utterance = new SpeechSynthesisUtterance(sent);
                        if (selectedVoice) utterance.voice = selectedVoice;
                        utterance.lang = 'es-MX';
                        utterance.pitch = sentenceProfile.pitch;
                        utterance.rate = sentenceProfile.rate;
                        utterance.onend = resolve;
                        utterance.onerror = resolve;
                        speechSynthesis.speak(utterance);
                    });
                }

                stopLipSync();
                applyVisualState(getEmotionalProfile("neutral"));
            }

            function captureFrame() {
                if (!visionEnabled || !video.videoWidth) return null;
                canvas.width = video.videoWidth; canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);
                return canvas.toDataURL('image/jpeg').split(',')[1];
            }

            function handleKey(e) { if (e.key === 'Enter') send(); }

            async function send() {
                let inp = document.getElementById('inp');
                let text = inp.value.trim();
                if (!text) return;

                let base64Image = captureFrame();
                chatHistory.push({sender: 'user', text: text});
                inp.value = '';

                let randomThink = thinkingPhrases[Math.floor(Math.random() * thinkingPhrases.length)];
                document.getElementById('response-text').innerText = randomThink;
                applyVisualState(getEmotionalProfile("hmm analizando"));

                try {
                    let payload = { history: chatHistory };
                    if (base64Image) payload.image = base64Image;

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
                    localStorage.setItem('aurora_memory', JSON.stringify(chatHistory));
                    
                    await expressResponse(data.reply);

                } catch (error) {
                    document.getElementById('response-text').innerText = "Hmm... interrupción temporal de red.";
                    applyVisualState(getEmotionalProfile("error"));
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
    
    if not GEMINI_KEY:
        return {"reply": "Error: GEMINI_API_KEY no configurada."}

    try:
        # Modelos oficiales y estables actualizados compatibles con la API
        models_to_try = [
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "models/gemini-2.0-flash",
            "models/gemini-1.5-flash"
        ]
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
                model = genai.GenerativeModel(model_name=m_name, system_instruction=SYSTEM_PROMPT)
                chat_session = model.start_chat(history=gemini_history)
                response = chat_session.send_message(message_parts)
                break
            except Exception as e:
                last_error = str(e)
                continue
                
        if not response:
            return {"reply": f"Hmm... fallo en los servidores: {last_error}"}

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
        return {"reply": final_reply.strip()}

    except Exception as e:
        return {"reply": f"Hmm... error neuronal: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
