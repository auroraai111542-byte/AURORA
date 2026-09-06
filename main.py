import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

SYSTEM_PROMPT = """Eres F.R.I.D.A.Y. (Aurora), la IA avanzada de asistencia táctica y ejecutiva. 
Eres extremadamente inteligente, rápida, eficiente, ligeramente sarcástica y con una precisión impecable estilo Iron Man. 
Responde de forma ultra concisa, directa y con total solvencia técnica."""

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
            
            /* HUD Holográfico en el Fondo */
            .bg-face-container {
                position: absolute;
                top: 0; left: 0; width: 100%; height: 100%;
                overflow: hidden;
                z-index: 0;
                pointer-events: none;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            /* Rostro Estético Estilo HUD / F.R.I.D.A.Y. */
            .face { 
                width: 180px; height: 180px; 
                background: radial-gradient(circle, rgba(56,189,248,0.15) 0%, rgba(37,99,235,0.05) 70%, transparent 100%); 
                border-radius: 50%; 
                position: absolute; 
                opacity: 0.35; 
                box-shadow: 0 0 40px rgba(56, 189, 248, 0.25), inset 0 0 25px rgba(56, 189, 248, 0.3); 
                border: 1px dashed rgba(56, 189, 248, 0.4);
                animation: hud-pulse 6s ease-in-out infinite alternate, hud-rotate 40s linear infinite;
            }
            .hud-ring {
                position: absolute;
                width: 220px; height: 220px;
                border: 2px solid rgba(56, 189, 248, 0.15);
                border-radius: 50%;
                border-top-color: #38bdf8;
                animation: hud-rotate-rev 15s linear infinite;
            }
            .eye { 
                width: 14px; height: 14px; 
                background: #38bdf8; 
                border-radius: 50%; 
                position: absolute; 
                top: 70px; 
                box-shadow: 0 0 10px #38bdf8;
                animation: blink 4s infinite; 
            }
            .eye.left { left: 52px; }
            .eye.right { right: 52px; }
            .mouth { 
                width: 40px; height: 4px; 
                background: #38bdf8; 
                border-radius: 4px; 
                position: absolute; 
                bottom: 50px; 
                left: 70px; 
                box-shadow: 0 0 8px #38bdf8;
                transition: height 0.08s, width 0.08s, border-radius 0.08s; 
            }
            .mouth.talking { animation: talk 0.12s infinite alternate !important; }
            
            @keyframes blink { 0%, 96%, 98%, 100% { transform: scaleY(1); } 97% { transform: scaleY(0.1); } }
            @keyframes talk { 0% { height: 4px; width: 40px; border-radius: 4px; } 100% { height: 16px; width: 34px; border-radius: 8px; } }
            @keyframes hud-pulse { 0% { transform: scale(0.95); opacity: 0.25; } 100% { transform: scale(1.05); opacity: 0.45; } }
            @keyframes hud-rotate { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes hud-rotate-rev { 0% { transform: rotate(360deg); } 100% { transform: rotate(0deg); } }

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

            .msg { 
                padding: 12px 16px; 
                border-radius: 14px; 
                max-width: 85%; 
                line-height: 1.5; 
                font-size: 0.95rem; 
                word-break: break-word; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                backdrop-filter: blur(8px);
            }
            .user .msg { 
                background: linear-gradient(135deg, #0284c7, #0369a1); 
                color: #ffffff; 
                border-bottom-right-radius: 4px; 
                border: 1px solid rgba(56,189,248,0.3);
            }
            .bot .msg { 
                background: rgba(15, 23, 42, 0.85); 
                color: #e2e8f0; 
                border: 1px solid rgba(56, 189, 248, 0.2); 
                border-bottom-left-radius: 4px; 
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
        <div class="bg-face-container">
            <div style="position: relative; width: 220px; height: 220px; display: flex; align-items: center; justify-content: center;">
                <div class="hud-ring"></div>
                <div class="face">
                    <div class="eye left"></div>
                    <div class="eye right"></div>
                    <div class="mouth" id="mouth"></div>
                </div>
            </div>
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
                <div class="msg">Sistemas en línea a máxima velocidad. Protocolo F.R.I.D.A.Y. activado. ¿Qué orden ejecutamos ahora? ⚡</div>
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

            function speak(text) {
                if (!voiceEnabled) return;
                speechSynthesis.cancel();
                let cleanText = text.replace(/[*_~]/g, ''); 
                currentUtterance = new SpeechSynthesisUtterance(cleanText);
                currentUtterance.lang = 'es-MX';
                // Tono y velocidad optimizados para sonar ágil y nítido estilo F.R.I.D.A.Y.
                currentUtterance.pitch = 1.25; 
                currentUtterance.rate = 1.15;
                
                let voices = speechSynthesis.getVoices();
                let crispVoice = voices.find(v => v.lang.includes('es') && (v.name.toLowerCase().includes('google') || v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('sara')));
                if (crispVoice) currentUtterance.voice = crispVoice;

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
                    chat.innerHTML += `<div class="message-row bot"><div class="msg">Error de enlace con el servidor principal.</div></div>`;
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
