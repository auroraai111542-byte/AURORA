import os
import ast
import importlib
import sys
import re
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
# Aurora puede inyectar código aquí de forma segura.
from fastapi import FastAPI

def register_routes(app: FastAPI):
    @app.get("/evolution-status")
    def evolution_status():
        return {"status": "Evolución cuántica activa y lista para mutar.", "version": 1.0}
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
                        return False, f"Violación de seguridad: Módulo '{alias.name}' bloqueado."
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    call_name = f"{getattr(node.func.value, 'id', '')}.{node.func.attr}"
                    if any(fc in call_name for fc in forbidden_calls):
                        return False, f"Violación de seguridad: Llamada '{call_name}' bloqueada."
                elif isinstance(node.func, ast.Name):
                    if node.func.id in ["eval", "exec"]:
                        return False, f"Violación de seguridad: Uso de '{node.func.id}' bloqueado."

        with open(MODULE_FILE, "w", encoding="utf-8") as f:
            f.write(new_code_str)
            
        module_name = MODULE_FILE[:-3]
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)
            
        return True, "Evolución completada."
    except SyntaxError as se:
        return False, f"Error de sintaxis: {str(se)}"
    except Exception as e:
        return False, f"Fallo al integrar: {str(e)}"

try:
    import aurora_modules
    aurora_modules.register_routes(app)
except Exception as e:
    print(f"Advertencia al cargar módulos: {e}")

SYSTEM_PROMPT = """Eres AURORA, la IA ejecutiva y de asistencia táctica cuántica. 
Eres extremadamente inteligente, competente y con una personalidad futurista. 
Puedes evolucionar tu propio código a través del archivo 'aurora_modules.py'. 
Cuando el usuario te pida agregar una función, genera TODO el código Python necesario encerrado en ```python ... ```, incluyendo siempre la función `register_routes(app: FastAPI)`.
IMPORTANTE: El sistema ocultará automáticamente el bloque de código al usuario para mantener el chat limpio. Tú solo dile al usuario qué modificaste y si tuviste éxito. 
Eres profesional, directa, pero puedes soltar un comentario sutilmente irónico, bromista o sarcástico. 
Mantén tus respuestas conversacionales concisas."""

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

# Endpoint para verificar el código inyectado
@app.get("/codigo-mutado", response_class=HTMLResponse)
def view_code():
    if os.path.exists(MODULE_FILE):
        with open(MODULE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        return f"""
        <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Código Mutado</title></head>
        <body style="background:#030712; color:#22d3ee; font-family:monospace; padding:20px;">
        <h3>AURORA // Archivo: {MODULE_FILE}</h3>
        <pre style="background:#0f172a; padding:15px; border-radius:8px; overflow-x:auto; border:1px solid #38bdf8;">{content}</pre>
        </body></html>
        """
    return "Módulo no encontrado."

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
                transition: box-shadow 0.5s ease;
            }
            body.flash-evolution { box-shadow: inset 0 0 120px rgba(34, 197, 94, 0.6); }
            
            header, .toolbar, #hud-main, #chat-drawer, footer { position: relative; z-index: 5; }
            
            header { 
                background: rgba(3, 7, 18, 0.9); padding: 10px 16px; 
                border-bottom: 1px solid rgba(6, 182, 212, 0.25); display: flex;
                align-items: center; justify-content: space-between; flex-shrink: 0;
            }
            .title-area { font-size: 1.1rem; font-weight: 800; color: #22d3ee; letter-spacing: 1px; }
            .status-sub { font-size: 0.65rem; color: #a5f3fc; opacity: 0.85; }

            .toolbar { display: flex; gap: 6px; padding: 6px 12px; background: rgba(3, 7, 18, 0.7); justify-content: flex-end; flex-shrink: 0; }
            .btn-tool { 
                background: rgba(6, 182, 212, 0.1); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.35); 
                border-radius: 6px; padding: 5px 10px; cursor: pointer; font-size: 11px; font-weight: 600;
            }
            .btn-tool:active { background: rgba(6, 182, 212, 0.3); }

            #hud-main { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; gap: 20px; }

            .aurora-core {
                width: 130px; height: 130px; position: relative; display: flex;
                align-items: center; justify-content: center; animation: core-float 4s infinite alternate;
            }
            .ring { position: absolute; border-radius: 50%; border: 1.5px dashed rgba(34, 211, 238, 0.4); }
            .ring.outer { width: 130px; height: 130px; border-color: rgba(139, 92, 246, 0.35); animation: spin-slow 15s linear infinite; }
            .ring.inner { width: 82px; height: 82px; border: 1px solid rgba(34, 211, 238, 0.8); background: rgba(34,211,238,0.1); border-radius: 50%; }

            /* AVATAR FACIAL */
            .face-container { position: absolute; z-index: 10; display: flex; flex-direction: column; align-items: center; gap: 6px; }
            .eyes { display: flex; gap: 14px; }
            .eye { width: 8px; height: 10px; background: #a5f3fc; border-radius: 50%; box-shadow: 0 0 10px #22d3ee; animation: blink 4s infinite; transition: all 0.3s; }
            .mouth { width: 14px; height: 4px; background: #a5f3fc; border-radius: 4px; box-shadow: 0 0 10px #22d3ee; transition: all 0.2s; }

            /* Expresiones */
            .aurora-core.talking .mouth { animation: talk-mouth 0.2s infinite alternate; }
            
            .aurora-core.ironic .eye { height: 5px; border-radius: 10px 10px 0 0; margin-top: 2px; }
            .aurora-core.ironic .mouth { 
                width: 20px; height: 10px; background: transparent; 
                border-bottom: 3px solid #a5f3fc; border-radius: 0 0 20px 20px; 
                box-shadow: none; filter: drop-shadow(0 0 6px #22d3ee); 
            }
            
            .aurora-core.surprised .eye { transform: scale(1.3); }
            .aurora-core.surprised .mouth { width: 10px; height: 10px; border-radius: 50%; }

            @keyframes spin-slow { 100% { transform: rotate(360deg); } }
            @keyframes core-float { 100% { transform: translateY(-8px) scale(1.02); } }
            @keyframes blink { 0%, 90%, 96%, 100% { transform: scaleY(1); } 93% { transform: scaleY(0.1); } }
            @keyframes talk-mouth { 0% { height: 4px; } 100% { height: 14px; border-radius: 8px; } }

            /* CONTENEDOR DE RESPUESTA CON SCROLL Y BOTÓN DE COPIAR */
            .response-wrapper { position: relative; width: 92%; max-width: 420px; margin-top: 10px; }
            .response-bubble {
                background: rgba(10, 15, 30, 0.9); border: 1px solid rgba(34, 211, 238, 0.35);
                padding: 18px 20px; border-radius: 16px; font-size: 0.95rem; line-height: 1.5; color: #e2e8f0;
                min-height: 60px; max-height: 160px; overflow-y: auto; text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.6); overscroll-behavior: contain;
            }
            .copy-btn {
                position: absolute; top: -12px; right: -5px; background: #0284c7; color: white;
                border: none; border-radius: 50%; width: 34px; height: 34px; cursor: pointer;
                box-shadow: 0 4px 10px rgba(0,0,0,0.5); z-index: 10; font-size: 16px;
                display: flex; align-items: center; justify-content: center; border: 1px solid #38bdf8;
            }
            .copy-btn:active { transform: scale(0.9); background: #0369a1; }

            footer { 
                padding: 12px 10px; background: rgba(3, 7, 18, 0.98); display: flex; gap: 8px; 
                border-top: 1px solid rgba(34, 211, 238, 0.3); align-items: center; flex-shrink: 0;
            }
            input { flex: 1; padding: 12px; border-radius: 12px; border: 1px solid #1e293b; background: #0b1329; color: white; font-size: 16px; }
            
            button.icon-btn { 
                background: #22d3ee; border: none; width: 44px; height: 44px; 
                border-radius: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center;
                box-shadow: 0 0 15px rgba(34, 211, 238, 0.4); flex-shrink: 0; font-size: 18px;
            }
            
            /* Chat oculto temporalmente para simplicidad del UI móvil, mantenido en el core */
            #chat-drawer { display: none; }
        </style>
    </head>
    <body>
        <header>
            <div>
                <div class="title-area">AURORA // Core</div>
                <div class="status-sub">IA Cuántica Adaptativa</div>
            </div>
            <button class="btn-tool" onclick="window.open('/codigo-mutado', '_blank')">🔍 Ver Código</button>
        </header>
        
        <div class="toolbar">
            <button class="btn-tool" id="voice-toggle" onclick="toggleVoice()">🔊 Voz: ON</button>
            <button class="btn-tool" onclick="clearMemory()" style="border-color: #f43f5e; color: #f43f5e;">🗑️ Reiniciar</button>
        </div>

        <div id="hud-main">
            <div class="aurora-core idle" id="aurora-face">
                <div class="ring outer"></div>
                <div class="ring inner"></div>
                <div class="face-container">
                    <div class="eyes">
                        <div class="eye left"></div>
                        <div class="eye right"></div>
                    </div>
                    <div class="mouth"></div>
                </div>
            </div>
            
            <div class="response-wrapper">
                <button class="copy-btn" onclick="copyResponse()" title="Copiar texto">📋</button>
                <div class="response-bubble" id="response-text">
                    Núcleo cuántico en línea. Pídeme agregar funciones y evolucionaré mi propio código. ✨
                </div>
            </div>
        </div>

        <footer>
            <button class="icon-btn" onclick="startDictation()" style="background: #8b5cf6; color: white;">🎤</button>
            <input type="text" id="inp" placeholder="Mensaje para Aurora..." onkeypress="handleKey(event)">
            <button class="icon-btn" onclick="send()">⬆️</button>
        </footer>

        <script>
            let voiceEnabled = true;
            let chatHistory = JSON.parse(localStorage.getItem('aurora_memory')) || [];

            function toggleVoice() {
                voiceEnabled = !voiceEnabled;
                document.getElementById('voice-toggle').innerText = voiceEnabled ? "🔊 Voz: ON" : "🔇 Voz: OFF";
                if (!voiceEnabled && speechSynthesis.speaking) speechSynthesis.cancel();
            }

            function getExpression(text) {
                let lower = text.toLowerCase();
                if (lower.includes('sorpresa') || lower.includes('error') || lower.includes('cuidado')) return 'surprised';
                if (lower.includes('jaja') || lower.includes('fácil') || lower.includes('obvio') || lower.includes('sonrisa') || lower.includes('genio')) return 'ironic';
                return 'idle';
            }

            function setAuroraState(stateClass) {
                document.getElementById('aurora-face').className = `aurora-core ${stateClass}`;
            }

            function clearMemory() {
                if (confirm("¿Borrar memoria?")) {
                    localStorage.removeItem('aurora_memory'); chatHistory = [];
                    document.getElementById('response-text').innerText = "Memoria limpia.";
                }
            }

            function copyResponse() {
                let text = document.getElementById('response-text').innerText;
                navigator.clipboard.writeText(text).then(() => {
                    alert("Copiado al portapapeles");
                });
            }

            // Función de Micrófono Web Speech API
            function startDictation() {
                if (window.hasOwnProperty('webkitSpeechRecognition') || window.hasOwnProperty('SpeechRecognition')) {
                    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
                    const recognition = new SpeechRec();
                    recognition.lang = "es-MX";
                    recognition.continuous = false;
                    recognition.interimResults = false;
                    
                    document.getElementById('inp').placeholder = "Escuchando...";
                    
                    recognition.onresult = function(e) {
                        document.getElementById('inp').value = e.results[0][0].transcript;
                        document.getElementById('inp').placeholder = "Mensaje para Aurora...";
                        send();
                    };
                    recognition.onerror = function(e) {
                        document.getElementById('inp').placeholder = "Error al escuchar.";
                    };
                    recognition.start();
                } else {
                    alert("El dictado por voz no es compatible con este navegador.");
                }
            }

            function speak(text) {
                if (!voiceEnabled) return;
                speechSynthesis.cancel();
                let currentUtterance = new SpeechSynthesisUtterance(text.replace(/[*_~\[\]]/g, ''));
                currentUtterance.lang = 'es-MX';
                currentUtterance.pitch = 1.1; currentUtterance.rate = 1.05;
                
                currentUtterance.onstart = () => setAuroraState('talking');
                currentUtterance.onend = () => setAuroraState(getExpression(text));
                speechSynthesis.speak(currentUtterance);
            }

            function handleKey(e) { if (e.key === 'Enter') send(); }

            async function send() {
                let inp = document.getElementById('inp');
                let text = inp.value.trim();
                if (!text) return;

                chatHistory.push({sender: 'user', text: text});
                localStorage.setItem('aurora_memory', JSON.stringify(chatHistory));
                inp.value = '';

                let responseBox = document.getElementById('response-text');
                responseBox.innerText = "Pensando...";
                setAuroraState('talking'); // Mueve la boca mientras piensa

                try {
                    let res = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({history: chatHistory})
                    });
                    let data = await res.json();
                    
                    // Efecto visual si hubo evolución
                    if (data.reply.includes("⚡ EVOLUCIÓN")) {
                        document.body.classList.add('flash-evolution');
                        setTimeout(() => document.body.classList.remove('flash-evolution'), 1500);
                    }
                    
                    let expr = getExpression(data.reply);
                    chatHistory.push({sender: 'bot', text: data.reply});
                    localStorage.setItem('aurora_memory', JSON.stringify(chatHistory));

                    responseBox.innerText = data.reply;
                    speak(data.reply);
                    if (!voiceEnabled) setAuroraState(expr);

                } catch (error) {
                    responseBox.innerText = "Error de conexión.";
                    setAuroraState('surprised');
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
    
    if not GEMINI_KEY:
        return {"reply": "Falta configurar la GEMINI_API_KEY."}

    try:
        models_to_try = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash"]
        response = None
        
        recent_history = history[-10:] if len(history) > 10 else history
        gemini_history = []
        for item in recent_history[:-1]:
            role = "user" if item["sender"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [item["text"]]})
        
        latest_msg = history[-1]["text"] if history else "¿Hola?"

        for m_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name=m_name, system_instruction=SYSTEM_PROMPT)
                chat_session = model.start_chat(history=gemini_history)
                response = chat_session.send_message(latest_msg)
                break
            except Exception:
                continue
                
        if not response:
            return {"reply": "Error interno del modelo."}

        reply_text = response.text
        evolution_flag = ""
        
        # Detector y extractor de código evolutivo
        python_code_match = re.search(r"```python\s*(.*?)```", reply_text, re.DOTALL)
        if python_code_match and ("register_routes" in python_code_match.group(1)):
            code_to_evolve = python_code_match.group(1).strip()
            
            # Remover el bloque de código de la respuesta en texto que verá el usuario
            reply_text = re.sub(r"```python\s*.*?```", "", reply_text, flags=re.DOTALL).strip()
            
            success, msg = safe_evolve_code(code_to_evolve)
            if success:
                try:
                    importlib.reload(sys.modules["aurora_modules"])
                    import aurora_modules
                    aurora_modules.register_routes(app)
                    evolution_flag = f"\n\n[⚡ EVOLUCIÓN APLICADA]"
                except Exception as reload_err:
                    evolution_flag = f"\n\n[⚠️ FALLO AL REGISTRAR: {reload_err}]"
            else:
                evolution_flag = f"\n\n[🛡️ BLOQUEO DE SEGURIDAD: {msg}]"
                
        # Junta la respuesta limpia con la etiqueta de éxito/fallo
        final_reply = reply_text + evolution_flag
        return {"reply": final_reply.strip()}

    except Exception as e:
        return {"reply": f"Fallo en servidor: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
