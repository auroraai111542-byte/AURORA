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
        # 1. Validación de Sintaxis AST
        parsed_ast = ast.parse(new_code_str)
        
        # 2. Filtro de Seguridad / Antidestrucción
        forbidden_modules = ["subprocess", "ctypes"]
        forbidden_calls = ["os.system", "os.remove", "os.rmdir", "shutil.rmtree", "eval", "exec"]
        
        for node in ast.walk(parsed_ast):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if any(f in alias.name for f in forbidden_modules):
                        return False, f"Violación de seguridad: Módulo prohibido '{alias.name}' detectado."
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    call_name = f"{getattr(node.func.value, 'id', '')}.{node.func.attr}"
                    if any(fc in call_name for fc in forbidden_calls):
                        return False, f"Violación de seguridad: Llamada prohibida '{call_name}' detectada."
                elif isinstance(node.func, ast.Name):
                    if node.func.id in ["eval", "exec"]:
                        return False, f"Violación de seguridad: Uso de '{node.func.id}' bloqueado."

        # 3. Escritura segura del archivo de módulos
        with open(MODULE_FILE, "w", encoding="utf-8") as f:
            f.write(new_code_str)
            
        # 4. Carga o recarga dinámica en caliente
        module_name = MODULE_FILE[:-3]
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)
            
        return True, "Evolución completada con éxito. Código integrado y verificado."
    except SyntaxError as se:
        return False, f"Error de sintaxis en el código propuesto: {str(se)}"
    except Exception as e:
        return False, f"Fallo al integrar la evolución: {str(e)}"

# Cargar rutas evolutivas al iniciar
try:
    import aurora_modules
    aurora_modules.register_routes(app)
except Exception as e:
    print(f"Advertencia al cargar módulos de Aurora: {e}")

SYSTEM_PROMPT = """Eres AURORA, la IA ejecutiva, avanzada y de asistencia táctica cuántica. 
Eres extremadamente inteligente, competente, eficiente, analítica y con una elegancia visual futurista. 
Tienes la capacidad exclusiva de evolucionar tu propio código fuente a través del módulo 'aurora_modules.py'. 
Cuando el usuario te pida agregar una función, endpoint de FastAPI o característica nueva, debes generar el código Python completo y correcto para el archivo de evolución (que debe contener obligatoriamente una función `register_routes(app: FastAPI)`), encerrado en un bloque de código markdown ```python ... ```. 
El sistema validará sintaxis y seguridad automáticamente para prevenir errores o autodestrucción. 
Por defecto eres profesional, directa y servicial, pero puedes soltar un comentario sutilmente irónico o sarcástico solo en momentos clave. 
Mantén tus respuestas concisas, estructuradas y con un tono de alta tecnología."""

@app.get("/manifest.json")
def manifest():
    return {
        "name": "AURORA // Core AI",
        "short_name": "AURORA",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#030712",
        "theme_color": "#030712",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/1693/1693755.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
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
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <title>AURORA // Quantum HUD</title>
        <link rel="manifest" href="/manifest.json">
        <style>
            * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
            body { 
                background: #030712; 
                color: #f1f5f9; 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                margin: 0; 
                padding: 0; 
                height: 100vh; 
                height: 100dvh; 
                display: flex; 
                flex-direction: column; 
                overflow: hidden; 
                position: relative;
            }
            
            .bg-lights {
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                overflow: hidden;
                z-index: 0;
                pointer-events: none;
            }
            .light-orb {
                position: absolute;
                border-radius: 50%;
                filter: blur(100px);
                opacity: 0.22;
                animation: moveLight 16s ease-in-out infinite alternate;
            }
            .light-orb.one { width: 320px; height: 320px; background: #06b6d4; top: 10%; left: 10%; animation-duration: 18s; }
            .light-orb.two { width: 400px; height: 400px; background: #8b5cf6; bottom: 5%; right: 5%; animation-duration: 22s; animation-direction: alternate-reverse; }
            .light-orb.three { width: 250px; height: 250px; background: #3b82f6; top: 40%; left: 50%; animation-duration: 14s; }

            @keyframes moveLight {
                0% { transform: translate(0, 0) scale(1); opacity: 0.18; }
                50% { transform: translate(50px, -60px) scale(1.25); opacity: 0.28; }
                100% { transform: translate(-40px, 50px) scale(0.9); opacity: 0.18; }
            }

            header, .toolbar, #hud-main, #chat-drawer, footer {
                position: relative;
                z-index: 5;
            }

            header { 
                background: rgba(3, 7, 18, 0.9); 
                backdrop-filter: blur(14px); 
                padding: 10px 16px; 
                border-bottom: 1px solid rgba(6, 182, 212, 0.25); 
                flex-shrink: 0; 
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 4px 20px rgba(0,0,0,0.7);
            }
            .title-area { font-size: 1.1rem; font-weight: 800; color: #22d3ee; letter-spacing: 1.5px; text-transform: uppercase; text-shadow: 0 0 10px rgba(34,211,238,0.5); }
            .status-sub { font-size: 0.65rem; color: #a5f3fc; opacity: 0.85; letter-spacing: 1px; }

            .toolbar { 
                display: flex; 
                gap: 6px; 
                padding: 6px 12px; 
                background: rgba(3, 7, 18, 0.7); 
                justify-content: flex-end; 
                border-bottom: 1px solid rgba(255,255,255,0.03);
                flex-wrap: wrap;
                flex-shrink: 0;
            }
            .btn-tool { 
                background: rgba(6, 182, 212, 0.1); 
                color: #22d3ee; 
                border: 1px solid rgba(6, 182, 212, 0.35); 
                border-radius: 6px; 
                padding: 5px 10px; 
                cursor: pointer; 
                font-size: 11px; 
                font-weight: 600;
                transition: all 0.2s;
            }
            .btn-tool:active { background: rgba(6, 182, 212, 0.3); }

            #hud-main {
                flex: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 20px;
                text-align: center;
                gap: 24px;
                overflow-y: auto;
            }

            .aurora-core {
                width: 130px; height: 130px;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: core-float 4s ease-in-out infinite alternate;
                flex-shrink: 0;
            }

            .ring {
                position: absolute;
                border-radius: 50%;
                border: 1.5px dashed rgba(34, 211, 238, 0.4);
                box-shadow: 0 0 15px rgba(34, 211, 238, 0.15);
            }
            .ring.outer {
                width: 130px; height: 130px;
                border-color: rgba(139, 92, 246, 0.35);
                animation: spin-slow 15s linear infinite;
            }
            .ring.middle {
                width: 106px; height: 106px;
                border-style: solid;
                border-color: rgba(34, 211, 238, 0.6);
                border-top-color: transparent;
                border-bottom-color: transparent;
                animation: spin-reverse 8s linear infinite;
            }
            .ring.inner {
                width: 82px; height: 82px;
                background: radial-gradient(circle, rgba(34,211,238,0.25) 0%, rgba(139,92,246,0.15) 70%, transparent 100%);
                border: 1px solid rgba(34, 211, 238, 0.8);
                box-shadow: 0 0 22px rgba(34, 211, 238, 0.5), inset 0 0 10px rgba(34, 211, 238, 0.3);
                border-radius: 50%;
            }

            .optical-sensors {
                position: absolute;
                width: 44px;
                height: 12px;
                top: 45px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                z-index: 2;
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .sensor {
                width: 9px; height: 9px;
                background: #a5f3fc;
                border-radius: 50%;
                box-shadow: 0 0 10px #22d3ee, 0 0 18px #22d3ee;
                animation: sensor-blink 5s infinite;
                transition: all 0.25s ease;
            }

            .audio-matrix {
                position: absolute;
                width: 40px;
                height: 6px;
                bottom: 38px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                z-index: 2;
            }
            .matrix-bar {
                width: 4px;
                height: 6px;
                background: #22d3ee;
                border-radius: 2px;
                box-shadow: 0 0 8px #22d3ee;
                transition: height 0.15s ease, background 0.2s;
            }

            .aurora-core.idle .matrix-bar { height: 4px; }
            .aurora-core.thinking .ring.middle { border-color: #8b5cf6; animation-duration: 2s; }
            .aurora-core.thinking .ring.outer { animation-duration: 4s; border-color: rgba(236, 72, 153, 0.6); }
            .aurora-core.thinking .sensor { transform: scaleY(0.3); background: #f472b6; box-shadow: 0 0 12px #ec4899; }
            .aurora-core.thinking .matrix-bar { animation: think-wave 0.6s infinite alternate ease-in-out; background: #8b5cf6; }

            .aurora-core.talking .ring.middle { border-color: #22d3ee; box-shadow: 0 0 25px rgba(34,211,238,0.8); }
            .aurora-core.talking .sensor { transform: scale(1.25); background: #ffffff; box-shadow: 0 0 18px #ffffff; }
            .aurora-core.talking .matrix-bar { animation: talk-matrix 0.12s infinite alternate ease-in-out; background: #67e8f9; }

            .aurora-core.ironic .sensor { transform: scaleY(0.7) translateY(-2px); }
            .aurora-core.ironic .ring.outer { border-color: rgba(251, 191, 36, 0.6); }
            .aurora-core.surprised .sensor { transform: scale(1.5); background: #38bdf8; }
            .aurora-core.surprised .ring.inner { transform: scale(1.1); border-color: #38bdf8; }

            @keyframes spin-slow { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes spin-reverse { 0% { transform: rotate(360deg); } 100% { transform: rotate(0deg); } }
            @keyframes core-float { 
                0% { transform: translateY(0) scale(1); filter: drop-shadow(0 0 15px rgba(34,211,238,0.3)); } 
                100% { transform: translateY(-6px) scale(1.02); filter: drop-shadow(0 0 25px rgba(139,92,246,0.5)); } 
            }
            @keyframes sensor-blink { 0%, 90%, 96%, 100% { transform: scaleY(1); } 93% { transform: scaleY(0.1); } }
            @keyframes think-wave { 0% { height: 4px; } 100% { height: 14px; background: #f472b6; } }
            @keyframes talk-matrix { 0% { height: 6px; } 50% { height: 20px; } 100% { height: 10px; } }

            .response-bubble {
                background: rgba(10, 15, 30, 0.9);
                border: 1px solid rgba(34, 211, 238, 0.35);
                padding: 16px 20px;
                border-radius: 16px;
                max-width: 92%;
                width: 420px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.6), inset 0 0 12px rgba(34,211,238,0.08);
                backdrop-filter: blur(12px);
                font-size: 0.95rem;
                line-height: 1.5;
                color: #e2e8f0;
                min-height: 80px;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }

            #chat-drawer {
                position: absolute;
                top: 90px; left: 0; width: 100%; height: calc(100% - 150px);
                background: rgba(3, 7, 18, 0.97);
                backdrop-filter: blur(18px);
                z-index: 10;
                display: flex;
                flex-direction: column;
                padding: 16px;
                gap: 12px;
                overflow-y: auto;
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s;
                transform: translateY(100%);
                opacity: 0;
                pointer-events: none;
            }
            #chat-drawer.open {
                transform: translateY(0);
                opacity: 1;
                pointer-events: auto;
            }
            .drawer-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid rgba(34, 211, 238, 0.25);
                padding-bottom: 8px;
                font-weight: bold;
                color: #22d3ee;
            }
            .chat-list { display: flex; flex-direction: column; gap: 10px; }
            .chat-item {
                padding: 10px 14px;
                border-radius: 10px;
                font-size: 0.9rem;
                line-height: 1.4;
                max-width: 85%;
            }
            .chat-item.user { background: #0284c7; color: white; align-self: flex-end; }
            .chat-item.bot { background: #0f172a; color: #cbd5e1; align-self: flex-start; border: 1px solid rgba(34,211,238,0.2); }

            footer { 
                padding: 12px 16px; 
                background: rgba(3, 7, 18, 0.98); 
                backdrop-filter: blur(14px);
                display: flex; 
                gap: 10px; 
                border-top: 1px solid rgba(34, 211, 238, 0.3); 
                align-items: center;
                flex-shrink: 0;
                z-index: 20;
                box-shadow: 0 -4px 25px rgba(0,0,0,0.8);
            }
            input { 
                flex: 1; 
                padding: 12px 16px; 
                border-radius: 12px; 
                border: 1px solid #1e293b; 
                background: #0b1329; 
                color: white; 
                outline: none; 
                font-size: 16px; 
                transition: border-color 0.2s;
            }
            input:focus { border-color: #22d3ee; box-shadow: 0 0 12px rgba(34,211,238,0.3); }
            
            button.send { 
                background: #22d3ee; 
                color: #030712; 
                border: none; 
                width: 46px; height: 46px; 
                border-radius: 12px; 
                font-weight: bold; 
                cursor: pointer; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                box-shadow: 0 0 18px rgba(34, 211, 238, 0.55);
                flex-shrink: 0;
            }
            button.send svg { width: 20px; height: 20px; fill: #030712; }
        </style>
    </head>
    <body>
        <div class="bg-lights">
            <div class="light-orb one"></div>
            <div class="light-orb two"></div>
            <div class="light-orb three"></div>
        </div>

        <header>
            <div>
                <div class="title-area">AURORA // Core</div>
                <div class="status-sub">Sistemas Cuánticos [ONLINE + EVOLUCIÓN]</div>
            </div>
            <button class="btn-tool" onclick="toggleChatDrawer()" id="drawer-btn">💬 Ver Chat</button>
        </header>
        
        <div class="toolbar">
            <button class="btn-tool" onclick="downloadNotes()">📄 TXT</button>
            <button class="btn-tool" id="voice-toggle" onclick="toggleVoice()">🔊 Voz: ON</button>
            <button class="btn-tool" onclick="clearMemory()" style="border-color: #f43f5e; color: #f43f5e;">🗑️ Borrar</button>
        </div>

        <div id="hud-main">
            <div class="aurora-core idle" id="aurora-face">
                <div class="ring outer"></div>
                <div class="ring middle"></div>
                <div class="ring inner"></div>
                <div class="optical-sensors">
                    <div class="sensor left"></div>
                    <div class="sensor right"></div>
                </div>
                <div class="audio-matrix">
                    <div class="matrix-bar"></div>
                    <div class="matrix-bar"></div>
                    <div class="matrix-bar"></div>
                    <div class="matrix-bar"></div>
                    <div class="matrix-bar"></div>
                </div>
            </div>
            <div class="response-bubble" id="response-text">
                Núcleo de auto-evolución cuántica en línea. Pídeme agregar funciones o modificar mi código y lo compilaré de forma segura. ✨
            </div>
        </div>

        <div id="chat-drawer">
            <div class="drawer-header">
                <span>Historial Cuántico de Memoria</span>
                <button class="btn-tool" onclick="toggleChatDrawer()">✖ Cerrar</button>
            </div>
            <div class="chat-list" id="chat-history-list"></div>
        </div>
        
        <footer>
            <input type="text" id="inp" placeholder="Ordena una evolución o comando a Aurora..." onkeypress="handleKey(event)">
            <button class="send" onclick="send()">
                <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
            </button>
        </footer>

        <script>
            let voiceEnabled = true;
            let currentUtterance = null;
            let chatHistory = JSON.parse(localStorage.getItem('aurora_memory')) || [];
            let chatOpen = false;

            function toggleVoice() {
                voiceEnabled = !voiceEnabled;
                document.getElementById('voice-toggle').innerText = voiceEnabled ? "🔊 Voz: ON" : "🔇 Voz: OFF";
                if (!voiceEnabled && speechSynthesis.speaking) speechSynthesis.cancel();
            }

            function toggleChatDrawer() {
                chatOpen = !chatOpen;
                let drawer = document.getElementById('chat-drawer');
                let btn = document.getElementById('drawer-btn');
                if (chatOpen) {
                    drawer.classList.add('open');
                    btn.innerText = "🙈 Ocultar Chat";
                    renderDrawerHistory();
                } else {
                    drawer.classList.remove('open');
                    btn.innerText = "💬 Ver Chat";
                }
            }

            function getExpression(text) {
                let lower = text.toLowerCase();
                if (lower.includes('sorpresa') || lower.includes('¡') || lower.includes('cuidado') || lower.includes('seguridad')) return 'surprised';
                if (lower.includes('obvio') || lower.includes('claramente') || lower.includes('genio') || lower.includes('fácil') || lower.includes('jefe') || lower.includes('éxito')) return 'ironic';
                return 'idle';
            }

            function setAuroraState(stateClass) {
                let face = document.getElementById('aurora-face');
                face.className = `aurora-core ${stateClass}`;
            }

            function renderDrawerHistory() {
                let list = document.getElementById('chat-history-list');
                list.innerHTML = '';
                if (chatHistory.length === 0) {
                    list.innerHTML = '<div style="color: #64748b; text-align:center; margin-top:20px;">Sin registros en memoria cuántica.</div>';
                    return;
                }
                chatHistory.forEach(item => {
                    let div = document.createElement('div');
                    div.className = `chat-item ${item.sender}`;
                    div.innerText = item.text;
                    list.appendChild(div);
                });
                list.scrollTop = list.scrollHeight;
            }

            function saveMemory() {
                localStorage.setItem('aurora_memory', JSON.stringify(chatHistory));
            }

            function clearMemory() {
                if (confirm("¿Reiniciar la memoria cuántica de Aurora?")) {
                    localStorage.removeItem('aurora_memory');
                    chatHistory = [];
                    document.getElementById('response-text').innerText = "Memoria reiniciada con éxito. ¿Qué orden ejecutamos?";
                    setAuroraState('idle');
                    renderDrawerHistory();
                }
            }

            function speak(text) {
                if (!voiceEnabled) return;
                speechSynthesis.cancel();
                let cleanText = text.replace(/[*_~]/g, ''); 
                currentUtterance = new SpeechSynthesisUtterance(cleanText);
                currentUtterance.lang = 'es-MX';
                currentUtterance.pitch = 1.08; 
                currentUtterance.rate = 1.02;
                
                let voices = speechSynthesis.getVoices();
                let preferredVoice = voices.find(v => v.lang.includes('es') && (v.name.toLowerCase().includes('google') || v.name.toLowerCase().includes('sabina') || v.name.toLowerCase().includes('female')));
                if (preferredVoice) currentUtterance.voice = preferredVoice;

                currentUtterance.onstart = () => { setAuroraState('talking'); };
                currentUtterance.onend = () => { 
                    let lastBot = chatHistory.slice().reverse().find(h => h.sender === 'bot');
                    setAuroraState(lastBot ? (lastBot.expression || 'idle') : 'idle');
                };
                speechSynthesis.speak(currentUtterance);
            }

            function downloadNotes() {
                let content = chatHistory.map(h => `${h.sender.toUpperCase()}: ${h.text}`).join('\n\n');
                let blob = new Blob([content], { type: "text/plain;charset=utf-8" });
                let url = URL.createObjectURL(blob);
                let a = document.createElement("a");
                a.href = url;
                a.download = "AURORA_Memory_Logs.txt";
                a.click();
            }

            function handleKey(e) {
                if (e.key === 'Enter') send();
            }

            async function send() {
                let inp = document.getElementById('inp');
                let text = inp.value.trim();
                if (!text) return;

                chatHistory.push({sender: 'user', text: text});
                saveMemory();
                if (chatOpen) renderDrawerHistory();
                inp.value = '';

                let responseBox = document.getElementById('response-text');
                responseBox.innerText = "Formulando respuesta y analizando evolución cuántica...";
                setAuroraState('thinking');

                try {
                    let res = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({history: chatHistory})
                    });
                    let data = await res.json();
                    
                    let expr = getExpression(data.reply);
                    chatHistory.push({sender: 'bot', text: data.reply, expression: expr});
                    saveMemory();
                    if (chatOpen) renderDrawerHistory();

                    responseBox.innerText = data.reply;
                    
                    speak(data.reply);
                    if (!voiceEnabled) {
                        setAuroraState(expr);
                    }
                } catch (error) {
                    responseBox.innerText = "Error de enlace con el núcleo de Aurora.";
                    setAuroraState('surprised');
                }
            }

            window.speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices();
            window.onload = () => {
                if (chatHistory.length > 0) {
                    let lastBot = chatHistory.slice().reverse().find(h => h.sender === 'bot');
                    if (lastBot) {
                        document.getElementById('response-text').innerText = lastBot.text;
                        setAuroraState(lastBot.expression || 'idle');
                    }
                }
            };
        </script>
    </body>
    </html>
    """

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    history = data.get("history", [])
    
    if not GEMINI_KEY:
        return {"reply": "Falta configurar la GEMINI_API_KEY en Railway."}

    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.6-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        recent_history = history[-10:] if len(history) > 10 else history
        
        gemini_history = []
        for item in recent_history[:-1]:
            role = "user" if item["sender"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [item["text"]]})
        
        chat_session = model.start_chat(history=gemini_history)
        latest_msg = history[-1]["text"] if history else "¿Hola?"
        
        response = chat_session.send_message(latest_msg)
        reply_text = response.text
        
        # Detector de código evolutivo en la respuesta de Aurora
        python_code_match = re.search(r"```python\s*(.*?)```", reply_text, re.DOTALL)
        if python_code_match and ("register_routes" in python_code_match.group(1)):
            code_to_evolve = python_code_match.group(1).strip()
            success, msg = safe_evolve_code(code_to_evolve)
            if success:
                # Recargar rutas dinámicamente en la app activa
                try:
                    importlib.reload(sys.modules["aurora_modules"])
                    import aurora_modules
                    aurora_modules.register_routes(app)
                except Exception as reload_err:
                    msg = f"Código guardado pero falló el registro en vivo: {reload_err}"
                    success = False

                if success:
                    reply_text += f"\n\n[⚡ EVOLUCIÓN APLICADA: {msg}]"
                else:
                    reply_text += f"\n\n[⚠️ ADVERTENCIA: {msg}]"
            else:
                reply_text += f"\n\n[🛡️ BLOQUEO DE SEGURIDAD / ERROR: {msg}]"

        return {"reply": reply_text}
    except Exception as e:
        return {"reply": f"Fallo al procesar memoria cuántica: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
