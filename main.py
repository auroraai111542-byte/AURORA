import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

SYSTEM_PROMPT = """Eres Aurora, una asistente de IA superinteligente, sarcástica, con un humor irónico pero muy empática. 
Estás diseñada para ser una asistente de bolsillo tipo viernes (Iron Man).
Responde de forma concisa, útil y con personalidad."""

@app.get("/", response_class=HTMLResponse)
def home():
    return r"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Aurora AI - Background Face</title>
        <style>
            * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
            body { 
                background: #090d16; 
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
            
            /* Rostro Animado en el Fondo (Libre movimiento) */
            .bg-face-container {
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                overflow: hidden;
                z-index: 0;
                pointer-events: none;
            }
            .face { 
                width: 130px; height: 130px; 
                background: linear-gradient(135deg, #38bdf8, #2563eb); 
                border-radius: 50%; 
                position: absolute; 
                opacity: 0.15; 
                box-shadow: 0 0 50px rgba(56, 189, 248, 0.5); 
                animation: drift 18s ease-in-out infinite alternate;
            }
            .eye { 
                width: 18px; height: 18px; 
                background: #090d16; 
                border-radius: 50%; 
                position: absolute; 
                top: 38px; 
                animation: blink 4s infinite; 
            }
            .eye.left { left: 32px; }
            .eye.right { right: 32px; }
            .mouth { 
                width: 45px; height: 12px; 
                background: #090d16; 
                border-radius: 0 0 20px 20px; 
                position: absolute; 
                bottom: 30px; 
                left: 42px; 
                transition: height 0.1s, border-radius 0.1s; 
            }
            .mouth.talking { animation: talk 0.18s infinite alternate !important; }
            
            @keyframes blink { 0%, 96%, 98%, 100% { transform: scaleY(1); } 97% { transform: scaleY(0.1); } }
            @keyframes talk { 0% { height: 12px; border-radius: 0 0 20px 20px; } 100% { height: 32px; border-radius: 20px; } }
            @keyframes drift {
                0% { transform: translate(5vw, 10vh) scale(0.9); }
                33% { transform: translate(55vw, 25vh) scale(1.1); }
                66% { transform: translate(25vw, 55vh) scale(1); }
                100% { transform: translate(60vw, 65vh) scale(1.05); }
            }

            /* Asegurar que los elementos del chat estén por encima del fondo */
            header, .toolbar, #chat, footer {
                position: relative;
                z-index: 1;
            }

            /* Header Minimalista */
            header { 
                background: rgba(15, 23, 42, 0.8); 
                backdrop-filter: blur(12px); 
                padding: 10px 16px; 
                border-bottom: 1px solid rgba(56, 189, 248, 0.15); 
                flex-shrink: 0; 
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            }
            .title-area { font-size: 1.05rem; font-weight: 700; color: #38bdf8; letter-spacing: 0.5px; }
            .status-sub { font-size: 0.7rem; color: #94a3b8; }

            /* Barra de Herramientas */
            .toolbar { 
                display: flex; 
                gap: 8px; 
                padding: 6px 16px; 
                background: rgba(15, 23, 42, 0.5); 
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

            /* Contenedor de Chat optimizado (Sin ocultar globos) */
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

            .msg { 
                padding: 12px 16px; 
                border-radius: 16px; 
                max-width: 85%; 
                line-height: 1.5; 
                font-size: 0.95rem; 
                word-break: break-word; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                backdrop-filter: blur(4px);
            }
            .user .msg { 
                background: linear-gradient(135deg, #0284c7, #0369a1); 
                color: #ffffff; 
                border-bottom-right-radius: 4px; 
            }
            .bot .msg { 
                background: rgba(30, 41, 59, 0.85); 
                color: #e2e8f0; 
                border: 1px solid rgba(255,255,255,0.07); 
                border-bottom-left-radius: 4px; 
            }

            /* Caja de entrada fija abajo (Evita que oculte el chat) */
            footer { 
                padding: 12px 16px; 
                background: rgba(15, 23, 42, 0.95); 
                backdrop-filter: blur(12px);
                display: flex; 
                gap: 10px; 
                border-top: 1px solid rgba(56, 189, 248, 0.15); 
                align-items: center;
                flex-shrink: 0;
                box-shadow: 0 -4px 20px rgba(0,0,0,0.5);
            }
            input { 
                flex: 1; 
                padding: 12px 16px; 
                border-radius: 12px; 
                border: 1px solid #334155; 
                background: #1e293b; 
                color: white; 
                outline: none; 
                font-size: 16px; 
                transition: border-color 0.2s;
            }
            input:focus { border-color: #38bdf8; }
            
            button.send { 
                background: #38bdf8; 
                color: #0f172a; 
                border: none; 
                width: 46px; height: 46px; 
                border-radius: 12px; 
                font-weight: bold; 
                cursor: pointer; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
                flex-shrink: 0;
            }
            button.send svg { width: 20px; height: 20px; fill: #0f172a; }
        </style>
    </head>
    <body>
        <!-- Rostro flotando libremente en el fondo como marca de agua -->
        <div class="bg-face-container">
            <div class="face" id="mouth-container">
                <div class="eye left"></div>
                <div class="eye right"></div>
                <div class="mouth" id="mouth"></div>
            </div>
        </div>

        <header>
            <div>
                <div class="title-area">Aurora AI</div>
                <div class="status-sub">Sistemas operativos • En línea</div>
            </div>
        </header>
        
        <div class="toolbar">
            <button class="btn-tool" onclick="downloadNotes()">📄 Descargar TXT</button>
            <button class="btn-tool" id="voice-toggle" onclick="toggleVoice()">🔊 Voz: ON</button>
        </div>

        <div id="chat">
            <div class="message-row bot">
                <div class="msg">¡Hola! Rostro movido al fondo con libre desplazamiento y problemas de scroll solucionados. ¿Qué hacemos ahora? 😎</div>
            </div>
        </div>
        
        <footer>
            <input type="text" id="inp" placeholder="Escribe un mensaje..." onkeypress="handleKey(event)">
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

            function speak(text) {
                if (!voiceEnabled) return;
                speechSynthesis.cancel();
                let cleanText = text.replace(/[*_~]/g, ''); 
                currentUtterance = new SpeechSynthesisUtterance(cleanText);
                currentUtterance.lang = 'es-MX';
                currentUtterance.pitch = 1.1;
                currentUtterance.rate = 1.05;
                
                let voices = speechSynthesis.getVoices();
                let femaleVoice = voices.find(v => v.lang.includes('es') && v.name.toLowerCase().includes('female'));
                if (femaleVoice) currentUtterance.voice = femaleVoice;

                currentUtterance.onstart = () => document.getElementById('mouth').classList.add('talking');
                currentUtterance.onend = () => document.getElementById('mouth').classList.remove('talking');
                speechSynthesis.speak(currentUtterance);
            }

            function downloadNotes() {
                let chatHistory = document.getElementById('chat').innerText;
                let blob = new Blob([chatHistory], { type: "text/plain;charset=utf-8" });
                let url = URL.createObjectURL(blob);
                let a = document.createElement("a");
                a.href = url;
                a.download = "Aurora_Chat.txt";
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
                document.getElementById('mouth').classList.add('talking');

                try {
                    let res = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: text})
                    });
                    let data = await res.json();
                    
                    document.getElementById('mouth').classList.remove('talking');
                    chat.innerHTML += `<div class="message-row bot"><div class="msg">${data.reply}</div></div>`;
                    chat.scrollTop = chat.scrollHeight;
                    speak(data.reply);
                } catch (error) {
                    document.getElementById('mouth').classList.remove('talking');
                    chat.innerHTML += `<div class="message-row bot"><div class="msg">Ups, error de red en el sistema.</div></div>`;
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
        return {"reply": "Oye, falta configurar la GEMINI_API_KEY en Railway."}

    try:
        model = genai.GenerativeModel('gemini-3.6-flash')
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nUsuario: {user_msg}")
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Fallo al generar respuesta: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
