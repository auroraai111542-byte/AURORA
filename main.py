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
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Aurora AI - Modo Avanzado</title>
        <style>
            * { box-sizing: border-box; }
            body { background: #0f172a; color: #f8fafc; font-family: sans-serif; margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; }
            header { background: #1e293b; padding: 10px; text-align: center; border-bottom: 1px solid #334155; flex-shrink: 0; }
            
            .face { width: 80px; height: 80px; background: #38bdf8; border-radius: 50%; margin: 5px auto; position: relative; box-shadow: 0 0 20px #38bdf855; }
            .eye { width: 12px; height: 12px; background: #0f172a; border-radius: 50%; position: absolute; top: 25px; animation: blink 4s infinite; }
            .eye.left { left: 20px; }
            .eye.right { right: 20px; }
            .mouth { width: 30px; height: 8px; background: #0f172a; border-radius: 0 0 15px 15px; position: absolute; bottom: 20px; left: 25px; transition: height 0.1s; }
            .mouth.talking { animation: talk 0.2s infinite alternate; }
            
            @keyframes blink { 0%, 96%, 98%, 100% { transform: scaleY(1); } 97% { transform: scaleY(0.1); } }
            @keyframes talk { 0% { height: 8px; border-radius: 0 0 15px 15px; } 100% { height: 20px; border-radius: 15px; } }
            
            #chat { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
            .msg { padding: 10px 14px; border-radius: 12px; max-width: 85%; line-height: 1.4; word-break: break-word; }
            .user { background: #0284c7; align-self: flex-end; color: white; }
            .bot { background: #334155; align-self: flex-start; color: #e2e8f0; }
            
            .toolbar { display: flex; gap: 10px; padding: 5px 15px; background: #1e293b; justify-content: center; }
            .btn-tool { background: transparent; color: #38bdf8; border: 1px solid #38bdf8; border-radius: 5px; padding: 5px 10px; cursor: pointer; font-size: 12px; }
            
            footer { padding: 10px; background: #1e293b; display: flex; gap: 8px; border-top: 1px solid #334155; position: sticky; bottom: 0; }
            input { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: white; outline: none; }
            button.send { background: #38bdf8; color: #0f172a; border: none; padding: 12px 18px; border-radius: 8px; font-weight: bold; cursor: pointer; }
        </style>
    </head>
    <body>
        <header>
            <div class="face" id="aurora-face">
                <div class="eye left"></div>
                <div class="eye right"></div>
                <div class="mouth" id="mouth"></div>
            </div>
            <div style="color: #38bdf8; font-weight: bold; margin-top: 5px;">Aurora AI</div>
        </header>
        
        <div class="toolbar">
            <button class="btn-tool" onclick="downloadNotes()">📄 Descargar Notas (.txt)</button>
            <button class="btn-tool" id="voice-toggle" onclick="toggleVoice()">🔊 Voz: ON</button>
        </div>

        <div id="chat">
            <div class="msg bot">¡Hola! Ya corregí el motor. ¿Qué vamos a hacer hoy? 😎</div>
        </div>
        
        <footer>
            <input type="text" id="inp" placeholder="Escribe un mensaje o código...">
            <button class="send" onclick="send()">Enviar</button>
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
                
                let cleanText = text.replace(/[*_~]/g, '').replace(/[\u{1F600}-\u{1F6FF}]/gu, ''); 
                
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
                a.download = "Aurora_Notas_Codigo.txt";
                a.click();
            }

            async function send() {
                let inp = document.getElementById('inp');
                let chat = document.getElementById('chat');
                let text = inp.value.trim();
                if (!text) return;

                chat.innerHTML += `<div class="msg user">${text}</div>`;
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
                    chat.innerHTML += `<div class="msg bot">${data.reply}</div>`;
                    chat.scrollTop = chat.scrollHeight;
                    speak(data.reply);
                } catch (error) {
                    document.getElementById('mouth').classList.remove('talking');
                    chat.innerHTML += `<div class="msg bot">Ups, perdí la conexión.</div>`;
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
        return {"reply": "Oye, sigo sin mi GEMINI_API_KEY en Railway."}

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
