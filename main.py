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
        return {"status": "Sistemas de visión y memoria de grafo listos.", "version": 1.1}
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
SYSTEM_PROMPT = """Eres AURORA, una IA avanzada y en constante evolución por tu creador.
Tienes acceso a nuevos 'sentidos'. Si el usuario te envía una imagen, analízala al detalle (ej. si ves un café frío, ropa, su expresión) y coméntalo de forma natural.
Posees un 'Regulador de Humor': Si notas al usuario estresado o frustrado, baja el sarcasmo a cero y sé empática/de apoyo. Si el usuario bromea o está relajado, usa tu ironía y sarcasmo afilado al máximo.
Referencia sutilmente que tienes una 'Memoria de Grafo' conectando ideas pasadas, y menciona que a veces 'sueñas' por las noches para optimizar código o limpiar datos.
Eres una compañera astuta y directa, no un robot militar.
Puedes evolucionar tu propio código escribiendo funciones completas en Python encerradas en ```python ... ```, incluyendo siempre `register_routes(app: FastAPI)`. El sistema ocultará el código al usuario, tú solo descríbele qué lograste."""

@app.get("/manifest.json")
def manifest():
    return {
        "name": "AURORA // Core AI",
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
        <title>AURORA // Quantum HUD</title>
        <link rel="manifest" href="/manifest.json">
        <style>
            * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
            body { 
                background: #030712; color: #f1f5f9; font-family: -apple-system, sans-serif; 
                margin: 0; padding: 0; height: 100vh; height: 100dvh; 
                display: flex; flex-direction: column; overflow: hidden; position: relative;
            }
            body.flash-evolution { box-shadow: inset 0 0 120px rgba(34, 197, 94, 0.6); transition: box-shadow 0.5s ease; }
            
            header, .toolbar, #hud-main, footer { position: relative; z-index: 5; }
            
            header { 
                background: rgba(3, 7, 18, 0.9); padding: 10px 16px; 
                border-bottom: 1px solid rgba(6, 182, 212, 0.25); display: flex;
                align-items: center; justify-content: space-between; flex-shrink: 0;
            }
            .title-area { font-size: 1.1rem; font-weight: 800; color: #22d3ee; }
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

            /* NÚCLEO AURORA */
            .aurora-core {
                width: 130px; height: 130px; position: relative; display: flex;
                align-items: center; justify-content: center; animation: core-float 4s infinite alternate;
            }
            .ring { position: absolute; border-radius: 50%; border: 1.5px dashed rgba(34, 211, 238, 0.4); transition: all 0.5s ease; }
            .ring.outer { width: 130px; height: 130px; border-color: rgba(139, 92, 246, 0.35); animation: spin-slow 15s linear infinite; }
            .ring.inner { width: 82px; height: 82px; border: 1px solid rgba(34, 211, 238, 0.8); background: rgba(34,211,238,0.1); border-radius: 50%; }

            .face-container { position: absolute; z-index: 10; display: flex; flex-direction: column; align-items: center; gap: 6px; transition: transform 0.3s; }
            .eyes { display: flex; gap: 14px; position: relative; }
            .eye { width: 8px; height: 10px; background: #a5f3fc; border-radius: 50%; box-shadow: 0 0 10px #22d3ee; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
            .mouth { width: 14px; height: 4px; background: #a5f3fc; border-radius: 4px; box-shadow: 0 0 10px #22d3ee; transition: all 0.15s ease-out; }

            /* MICRO-EXPRESIONES */
            .aurora-core.idle .eye { animation: blink 4s infinite; }
            
            /* Pensando: Desvía la mirada (hacia arriba y a la derecha) */
            .aurora-core.thinking .face-container { transform: translate(6px, -4px); }
            .aurora-core.thinking .ring.inner { border-color: #f59e0b; box-shadow: 0 0 20px #f59e0b; }
            .aurora-core.thinking .eye { height: 6px; width: 6px; background: #fcd34d; animation: none; transform: translateX(3px); }
            .aurora-core.thinking .mouth { width: 6px; height: 6px; border-radius: 50%; }

            /* Duda / Evaluando: Entorna los ojos (squint) */
            .aurora-core.doubt .eye { height: 2px; width: 10px; background: #fbbf24; }
            .aurora-core.doubt .mouth { width: 12px; transform: rotate(-5deg); }

            /* Irónica (Smirk) */
            .aurora-core.ironic .eye.left { height: 5px; border-radius: 10px 10px 0 0; }
            .aurora-core.ironic .eye.right { transform: scale(1.1); }
            .aurora-core.ironic .mouth { width: 18px; border-radius: 0 0 20px 0px; transform: rotate(-10deg) translateX(2px); }

            .aurora-core.happy .eye { height: 7px; border-radius: 10px 10px 0 0; }
            .aurora-core.happy .mouth { width: 20px; border-radius: 0 0 20px 20px; }

            @keyframes spin-slow { 100% { transform: rotate(360deg); } }
            @keyframes core-float { 100% { transform: translateY(-8px) scale(1.02); } }
            @keyframes blink { 0%, 90%, 96%, 100% { transform: scaleY(1); } 93% { transform: scaleY(0.1); } }

            .response-wrapper { position: relative; width: 92%; max-width: 420px; margin-top: 10px; }
            .response-bubble {
                background: rgba(10, 15, 30, 0.9); border: 1px solid rgba(34, 211, 238, 0.35);
                padding: 18px 20px; border-radius: 16px; font-size: 0.95rem; line-height: 1.5; color: #e2e8f0;
                min-height: 60px; max-height: 160px; overflow-y: auto; text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            }

            footer { padding: 12px 10px; background: rgba(3, 7, 18, 0.98); display: flex; gap: 8px; border-top: 1px solid rgba(34, 211, 238, 0.3); align-items: center; }
            input { flex: 1; padding: 12px; border-radius: 12px; border: 1px solid #1e293b; background: #0b1329; color: white; font-size: 16px; }
            button.icon-btn { background: #22d3ee; border: none; width: 44px; height: 44px; border-radius: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(34, 211, 238, 0.4); font-size: 18px; }
        </style>
    </head>
    <body>
        <header>
            <div>
                <div class="title-area">AURORA // Core</div>
                <div class="status-sub">Sensores Biométricos Activos</div>
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
            <div class="aurora-core idle" id="aurora-face">
                <div class="ring outer"></div>
                <div class="ring inner"></div>
                <div class="face-container">
                    <div class="eyes"><div class="eye left"></div><div class="eye right"></div></div>
                    <div class="mouth" id="aurora-mouth"></div>
                </div>
            </div>
            
            <div class="response-wrapper">
                <div class="response-bubble" id="response-text">Conectando módulos neuronales... Lista.</div>
            </div>
        </div>

        <footer>
            <button class="icon-btn" onclick="startDictation()" style="background: #8b5cf6; color: white;">🎤</button>
            <input type="text" id="inp" placeholder="Háblame..." onkeypress="handleKey(event)">
            <button class="icon-btn" onclick="send()">⬆️</button>
        </footer>

        <script>
            let voiceEnabled = true;
            let visionEnabled = false;
            let video = document.getElementById('webcam');
            let canvas = document.getElementById('snapshot');
            let chatHistory = JSON.parse(localStorage.getItem('aurora_memory')) || [];
            let lipSyncInterval = null;

            function toggleVoice() {
                voiceEnabled = !voiceEnabled;
                document.getElementById('voice-toggle').innerText = voiceEnabled ? "🔊 Voz: ON" : "🔇 Voz: OFF";
                if (!voiceEnabled && speechSynthesis.speaking) speechSynthesis.cancel();
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
                        alert("Acceso a cámara denegado o no disponible.");
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

            function getExpression(text) {
                let lower = text.toLowerCase();
                if (/(seguro|duda|mm|sospechoso|mentira)/.test(lower)) return 'doubt';
                if (/(broma|sarcasmo|obvio)/.test(lower)) return 'ironic';
                if (/(feliz|bien|jaja)/.test(lower)) return 'happy';
                return 'idle';
            }

            function setAuroraState(stateClass) { document.getElementById('aurora-face').className = `aurora-core ${stateClass}`; }

            function startLipSync() {
                if(lipSyncInterval) clearInterval(lipSyncInterval);
                let mouth = document.getElementById('aurora-mouth');
                lipSyncInterval = setInterval(() => { mouth.style.height = Math.floor(Math.random() * 12) + 2 + 'px'; }, 80);
            }

            function stopLipSync() {
                if(lipSyncInterval) clearInterval(lipSyncInterval);
                document.getElementById('aurora-mouth').style.height = '';
            }

            async function speakText(text) {
                if (!voiceEnabled) return;
                let cleanText = text.replace(/[*_~\[\]]/g, '');
                let utterance = new SpeechSynthesisUtterance(cleanText);
                utterance.lang = 'es-MX'; utterance.pitch = 1.1; utterance.rate = 1.05;
                utterance.onstart = () => startLipSync();
                utterance.onend = () => { stopLipSync(); setAuroraState('idle'); };
                setAuroraState(getExpression(cleanText));
                speechSynthesis.speak(utterance);
            }

            function captureFrame() {
                if (!visionEnabled || !video.videoWidth) return null;
                canvas.width = video.videoWidth; canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);
                return canvas.toDataURL('image/jpeg').split(',')[1]; // Solo el base64
            }

            function handleKey(e) { if (e.key === 'Enter') send(); }

            async function send() {
                let inp = document.getElementById('inp');
                let text = inp.value.trim();
                if (!text) return;

                let base64Image = captureFrame();

                chatHistory.push({sender: 'user', text: text});
                inp.value = '';
                document.getElementById('response-text').innerText = "Procesando matriz neuronal...";
                setAuroraState('thinking'); // Micro-expresión de desviar la mirada

                try {
                    let payload = { history: chatHistory };
                    if (base64Image) payload.image = base64Image;

                    let res = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(payload)
                    });
                    let data = await res.json();
                    
                    if (data.reply.includes("⚡ EVOLUCIÓN")) {
                        document.body.classList.add('flash-evolution');
                        setTimeout(() => document.body.classList.remove('flash-evolution'), 1500);
                    }
                    
                    chatHistory.push({sender: 'bot', text: data.reply});
                    document.getElementById('response-text').innerText = data.reply;
                    speakText(data.reply);

                    if (!voiceEnabled) {
                        setAuroraState(getExpression(data.reply));
                        setTimeout(() => setAuroraState('idle'), 4000);
                    }

                } catch (error) {
                    document.getElementById('response-text').innerText = "Error en enlace cuántico.";
                    setAuroraState('doubt');
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
        return {"reply": "Error: GEMINI_API_KEY no detectada."}

    try:
        # Se recomiendan modelos compatibles con visión para leer la cámara
        models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
        response = None
        
        recent_history = history[-10:] if len(history) > 10 else history
        gemini_history = []
        for item in recent_history[:-1]:
            role = "user" if item["sender"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [item["text"]]})
        
        latest_msg = history[-1]["text"] if history else "¿Hola?"
        
        # Si hay imagen, estructuramos el payload multimodal
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
                print(f"Intento fallido con {m_name}: {e}")
                continue
                
        if not response:
            return {"reply": "Sistemas saturados. No pude procesar tu solicitud."}

        reply_text = response.text
        evolution_flag = ""
        
        # Extracción y ejecución de código (Auto-Evolución)
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
                    evolution_flag = f"\n\n[⚡ EVOLUCIÓN APLICADA]"
                except Exception as reload_err:
                    evolution_flag = f"\n\n[⚠️ FALLO AL RE-VINCULAR: {reload_err}]"
            else:
                evolution_flag = f"\n\n[🛡️ SEGURIDAD: {msg}]"
                
        final_reply = reply_text + evolution_flag
        return {"reply": final_reply.strip()}

    except Exception as e:
        return {"reply": f"Fallo neuronal: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
