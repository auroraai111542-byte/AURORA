import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

SYSTEM_PROMPT = """Eres F.R.I.D.A.Y., la IA ejecutiva y táctica de asistencia avanzada. 
Eres extremadamente inteligente, competente, eficiente y analítica. 
Por defecto eres profesional, directa y servicial, pero puedes soltar un comentario sutilmente irónico o sarcástico solo en momentos clave o cuando la situación lo amerite, sin exagerar todo el tiempo. 
Mantén tus respuestas concisas, estructuradas y con tono de alta tecnología."""

@app.get("/", response_class=HTMLResponse)
def home():
    return r"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>F.R.I.D.A.Y. // Aurora HUD</title>
        <style>
            * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
            body { 
                background: #050b14; 
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
            
            /* Luces de Fondo Dinámicas (Iluminación ambiental en movimiento) */
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
                filter: blur(80px);
                opacity: 0.18;
                animation: moveLight 14s ease-in-out infinite alternate;
            }
            .light-orb.one {
                width: 280px; height: 280px;
                background: #38bdf8;
                top: 10%; left: 15%;
                animation-duration: 16s;
            }
            .light-orb.two {
                width: 350px; height: 350px;
                background: #2563eb;
                bottom: 10%; right: 10%;
                animation-duration: 20s;
                animation-direction: alternate-reverse;
            }
            .light-orb.three {
                width: 220px; height: 220px;
                background: #0ea5e9;
                top: 50%; left: 60%;
                animation-duration: 12s;
            }

            @keyframes moveLight {
                0% { transform: translate(0, 0) scale(1); opacity: 0.15; }
                50% { transform: translate(50px, -60px) scale(1.25); opacity: 0.25; }
                100% { transform: translate(-40px, 50px) scale(0.9); opacity: 0.15; }
            }

            header, .toolbar, #chat, footer {
                position: relative;
                z-index: 1;
            }

            header { 
                background: rgba(5, 11, 20, 0.85); 
                backdrop-filter: blur(12px); 
                padding: 10px 16px; 
                border-bottom: 1px solid rgba(56, 189, 248, 0.2); 
                flex-shrink: 0; 
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 4px 20px rgba(0,0,0,0.6);
            }
            .title-area { font-size: 1.05rem; font-weight: 700; color: #38bdf8; letter-spacing: 1px; text-transform: uppercase; }
            .status-sub { font-size: 0.65rem; color: #38bdf8; opacity: 0.8; letter-spacing: 0.5px; }

            .toolbar { 
                display: flex; 
                gap: 8px; 
                padding: 6px 16px; 
                background: rgba(5, 11, 20, 0.6); 
                justify-content: flex-end; 
                border-bottom: 1px solid rgba(255,255,255,0.03);
            }
            .btn-tool { 
                background: rgba(56, 189, 248, 0.1); 
                color: #38bdf8; 
                border: 1px solid rgba(56, 189, 248, 0.3); 
                border-radius: 6px; 
                padding: 4px 10px; 
                cursor: pointer; 
                font-size: 11px; 
                font-weight: 600;
            }
            .btn-tool:active { background: rgba(56, 189, 248, 0.3); }

            #chat { 
                flex: 1; 
                padding: 16px; 
                overflow-y: auto; 
                display: flex; 
                flex-direction: column; 
                gap: 16px; 
                scroll-behavior: smooth;
                padding-bottom: 20px;
            }
            
            .message-row { display: flex; width: 100%; gap: 10px; }
            .message-row.user { justify-content: flex-end; }
            .message-row.bot { justify-content: flex-start; }

            /* Contenedor del bot para alinear la cara holográfica arriba del globo */
            .bot-container {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                max-width: 85%;
                gap: 5px;
            }

            /* Mini Cara holográfica sobre el globo de diálogo del bot */
            .mini-face {
                width: 38px; height: 38px;
                background: radial-gradient(circle, rgba(56,189,248,0.25) 0%, rgba(37,99,235,0.1) 70%, transparent 100%);
                border-radius: 50%;
                position: relative;
                border: 1px solid rgba(56, 189, 248, 0.5);
                box-shadow: 0 0 12px rgba(56, 189, 248, 0.35);
                display: flex;
                align-items: center;
                justify-content: center;
                margin-left: 4px;
            }
            .mini-face .eye {
                width: 6px; height: 6px;
                background: #38bdf8;
                border-radius: 50%;
                position: absolute;
                top: 12px;
                box-shadow: 0 0 6px #38bdf8;
                animation: blink 4s infinite;
            }
            .mini-face .eye.left { left: 10px; }
            .mini-face .eye.right { right: 10px; }
            .mini-face .mouth {
                width: 14px; height: 3px;
                background: #38bdf8;
                border-radius: 2px;
                position: absolute;
                bottom: 10px;
                left: 12px;
                box-shadow: 0 0 5px #38bdf8;
                transition: height 0.08s, width 0.08s;
            }
            .mini-face.talking .mouth {
                animation: talk-mini 0.12s infinite alternate !important;
            }

            @keyframes blink { 0%, 96%, 98%, 100% { transform: scaleY(1); } 97% { transform: scaleY(0.1); } }
            @keyframes talk-mini { 0% { height: 3px; width: 14px; } 100% { height: 10px; width: 12px; } }

            .msg { 
                padding: 12px 16px; 
                border-radius: 14px; 
                line-height: 1.5; 
                font-size: 0.95rem; 
                word-break: break-word; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                backdrop-filter: blur(8px);
                width: 100%;
            }
            .user .msg { 
                background: linear-gradient(135deg, #0284c7, #0369a1); 
                color: #ffffff; 
                border-bottom-right-radius: 4px; 
                border: 1px solid rgba(56,189,248,0.3);
                max-width: 85%;
            }
            .bot .msg { 
                background: rgba(15, 23, 42, 0.85); 
                color: #e2e8f0; 
                border: 1px solid rgba(56, 189, 248, 0.2); 
                border-top-left-radius: 4px; 
            }

            footer { 
                padding: 12px 16px; 
                background: rgba(5, 11, 20, 0.95); 
                backdrop-filter: blur(12px);
                display: flex; 
                gap: 10px; 
                border-top: 1px solid rgba(56, 189, 248, 0.2); 
                align-items: center;
                flex-shrink: 0;
                box-shadow: 0 -4px 20px rgba(0,0,0,0.6);
            }
            input { 
                flex: 1; 
                padding: 12px 16px; 
                border-radius: 12px; 
                border: 1px solid #1e293b; 
                background: #0f172a; 
                color: white; 
                outline: none; 
                font-size: 16px; 
                transition: border-color 0.2s;
            }
            input:focus { border-color: #38bdf8; box-shadow: 0 0 10px rgba(56,189,248,0.2); }
            
            button.send { 
                background: #38bdf8; 
                color: #050b14; 
                border: none; 
                width: 46px; height: 46px; 
                border-radius: 12px; 
                font-weight: bold; 
                cursor: pointer; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                box-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
                flex-shrink: 0;
            }
            button.send svg { width: 20px; height: 20px; fill: #050b14; }
        </style>
    </head>
    <body>
        <!-- Luces de fondo dinámicas -->
        <div class="bg-lights">
            <div class="light-orb one"></div>
            <div class="light-orb two"></div>
            <div class="light-orb three"></div>
        </div>

        <header>
            <div>
                <div class="title-area">F.R.I.D.A.Y. // Aurora</div>
                <div class="status-sub">Sistemas tácticos activos [ONLINE]</div>
            </div>
        </header>
        
        <div class="toolbar">
            <button class="btn-tool" onclick="downloadNotes()">📄 Descargar TXT</button>
            <button class="btn-tool" id="voice-toggle" onclick="toggleVoice()">🔊 Voz: ON</button>
        </div>

        <div id="chat">
            <div class="message-row bot">
                <div class="bot-container">
                    <div class="mini-face" id="face-init">
                        <div class="eye left"></div>
                        <div class="eye right"></div>
                        <div class="mouth"></div>
                    </div>
                    <div class="msg">Sistemas en línea. Protocolo F.R.I.D.A.Y. activado. ¿Qué orden ejecutamos ahora? ⚡</div>
                </div>
            </div>
        </div>
        
        <footer>
            <input type="text" id="inp" placeholder="Escribe un comando o mensaje..." onkeypress="handleKey(event)">
            <button class="send" onclick="send()">
                <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path></svg>
            </button>
        </footer>

        <script>
            let voiceEnabled = true;
            let currentUtterance = null;

            function toggleVoice() {
                voiceEnabled = !voiceEnabled;
                document.getElementById('voice-toggle').innerText = voiceEnabled ? "🔊 Voz: ON" : "🔇 Voz: OFF";
                if (!voiceEnabled && speechSynthesis.speaking) speechSynthesis.cancel();
            }

            function speak(text, faceElem) {
                if (!voiceEnabled) return;
                speechSynthesis.cancel();
                let cleanText = text.replace(/[*_~]/g, ''); 
                currentUtterance = new SpeechSynthesisUtterance(cleanText);
                currentUtterance.lang = 'es-MX';
                // Voz menos robótica: tono equilibrado y velocidad natural y fluida
                currentUtterance.pitch = 1.05; 
                currentUtterance.rate = 1.02;
                
                let voices = speechSynthesis.getVoices();
                let preferredVoice = voices.find(v => v.lang.includes('es') && (v.name.toLowerCase().includes('google') || v.name.toLowerCase().includes('sabina') || v.name.toLowerCase().includes('female')));
                if (preferredVoice) currentUtterance.voice = preferredVoice;

                if (faceElem) {
                    currentUtterance.onstart = () => faceElem.classList.add('talking');
                    currentUtterance.onend = () => faceElem.classList.remove('talking');
                }
                speechSynthesis.speak(currentUtterance);
            }

            function downloadNotes() {
                let chatHistory = document.getElementById('chat').innerText;
                let blob = new Blob([chatHistory], { type: "text/plain;charset=utf-8" });
                let url = URL.createObjectURL(blob);
                let a = document.createElement("a");
                a.href = url;
                a.download = "FRIDAY_Aurora_Logs.txt";
                a.click();
            }

            function handleKey(e) {
                if (e.key === 'Enter') send();
            }

            async function send() {
                let inp = document.getElementById('inp');
                let chat = document.getElementById('chat');
                let text = inp.value.trim();
                if (!text) return;

                chat.innerHTML += `<div class="message-row user"><div class="msg">${text}</div></div>`;
                inp.value = '';
                chat.scrollTop = chat.scrollHeight;

                // Crear elemento burbuja bot con su propia mini cara arriba
                let botRow = document.createElement('div');
                botRow.className = 'message-row bot';
                
                let botContainer = document.createElement('div');
                botContainer.className = 'bot-container';
                
                let miniFace = document.createElement('div');
                miniFace.className = 'mini-face talking';
                miniFace.innerHTML = '<div class="eye left"></div><div class="eye right"></div><div class="mouth"></div>';
                
                let msgDiv = document.createElement('div');
                msgDiv.className = 'msg';
                msgDiv.innerText = 'Analizando solicitud...';

                botContainer.appendChild(miniFace);
                botContainer.appendChild(msgDiv);
                botRow.appendChild(botContainer);
                chat.appendChild(botRow);
                chat.scrollTop = chat.scrollHeight;

                try {
                    let res = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: text})
                    });
                    let data = await res.json();
                    
                    msgDiv.innerText = data.reply;
                    chat.scrollTop = chat.scrollHeight;
                    speak(data.reply, miniFace);
                } catch (error) {
                    miniFace.classList.remove('talking');
                    msgDiv.innerText = 'Error de enlace con el servidor principal.';
                    chat.scrollTop = chat.scrollHeight;
                }
            }

            window.speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices();
        </script>
    </body>
    </html>
    """

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_msg = data.get("message", "")
    
    if not GEMINI_KEY:
        return {"reply": "Falta configurar la GEMINI_API_KEY en Railway."}

    try:
        model = genai.GenerativeModel('gemini-3.6-flash')
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nUsuario: {user_msg}")
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Fallo al procesar orden: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
