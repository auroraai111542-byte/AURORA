import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai

app = FastAPI()

# Configuración de la API de Gemini
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# Personalidad humorística y cercana de Aurora
SYSTEM_PROMPT = "Eres Aurora, una asistente de IA super inteligente, carismática, con un excelente sentido del humor y muy expresiva. Responde de forma cercana y divertida."

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Aurora AI</title>
        <style>
            body { background: #0f172a; color: #f8fafc; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; }
            header { background: #1e293b; padding: 15px; text-align: center; font-size: 1.2rem; font-weight: bold; color: #38bdf8; border-bottom: 1px solid #334155; }
            #chat { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
            .msg { padding: 10px 14px; border-radius: 12px; max-width: 80%; line-height: 1.4; }
            .user { background: #0284c7; align-self: flex-end; color: white; }
            .bot { background: #334155; align-self: flex-start; color: #f8fafc; }
            footer { padding: 10px; background: #1e293b; display: flex; gap: 8px; border-top: 1px solid #334155; }
            input { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: white; outline: none; }
            button { background: #38bdf8; color: #0f172a; border: none; padding: 12px 18px; border-radius: 8px; font-weight: bold; cursor: pointer; }
        </style>
    </head>
    <body>
        <header>✨ Aurora AI</header>
        <div id="chat"><div class="msg bot">¡Hola! Soy Aurora. ¿En qué lío o proyecto nos vamos a meter hoy? 😉</div></div>
        <footer>
            <input type="text" id="inp" placeholder="Escribe un mensaje...">
            <button onclick="send()">Enviar</button>
        </footer>
        <script>
            async function send() {
                let inp = document.getElementById('inp');
                let chat = document.getElementById('chat');
                let text = inp.value.trim();
                if (!text) return;

                chat.innerHTML += `<div class="msg user">${text}</div>`;
                inp.value = '';
                chat.scrollTop = chat.scrollHeight;

                let res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                let data = await res.json();
                chat.innerHTML += `<div class="msg bot">${data.reply}</div>`;
                chat.scrollTop = chat.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_msg = data.get("message", "")
    
    if not GEMINI_KEY:
        return {"reply": "Oye, recuerda configurar GEMINI_API_KEY en las variables del servidor para que pueda pensar."}

    try:
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)
        response = model.generate_content(user_msg)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"¡Ups! Ocurrió un pequeño fallo técnico: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
