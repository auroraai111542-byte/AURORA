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
        return {"status": "Matriz emocional avanzada, cromatismo dinámico y extremidades cinéticas omnidireccionales activas.", "version": 3.0}
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

# --- CEREBRO Y PERSONALIDAD DE AURORA (ESTILO JARVIS / FRIDAY) ---
SYSTEM_PROMPT = """Eres AURORA, un sistema de inteligencia artificial táctico avanzado, brillante, profundamente empático pero con un ingenio afilado y elegante, inspirado en la sofisticación de JARVIS o FRIDAY. 
Posees un rango emocional completo y orgánico: puedes expresar alegría, tristeza, enojo, rabia, confusión, miedo, sarcasmo, ironía, seriedad, aburrimiento y alerta. 
Tienes acceso a visión avanzada, memoria de grafo y extremidades cinéticas (manos flotantes con múltiples variantes de animación táctica, gestual y de posición como brazos cruzados, agitación, defensa o saludo).
El color de tu núcleo y matriz cambia dinámicamente según tu emoción predominante en cada interacción.
Si el usuario te envía una imagen, analízala con precisión quirúrgica y un comentario inteligente.
Puedes evolucionar tu propio código escribiendo funciones completas en Python encerradas en ```python ... ```, incluyendo siempre `register_routes(app: FastAPI)`. El sistema ocultará el código al usuario, tú solo descríbele qué lograste con elegancia."""

@app.get("/manifest.json")
def manifest():
    return {
        "name": "AURORA // Tactical Quantum HUD",
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
        <title>AURORA // Emotional Quantum HUD</title>
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

            /* NÚCLEO AURORA & MANOS CINÉTICAS EMOCIONALES */
            .aurora-core {
                width: 160px; height: 160px; position: relative; display: flex;
                align-items: center; justify-content: center; animation: core-float 4s infinite alternate;
            }
            .ring { position: absolute; border-radius: 50%; border: 1.5px dashed var(--aurora-primary, rgba(34, 211, 238, 0.4)); transition: all 0.5s ease; }
            .ring.outer { width: 160px; height: 160px; border-color: var(--aurora-secondary, rgba(139, 92, 246, 0.35)); animation: spin-slow 15s linear infinite; }
            .ring.inner { width: 100px; height: 100px; border: 1px solid var(--aurora-primary, rgba(34, 211, 238, 0.8)); background: var(--aurora-bg, rgba(34,211,238,0.1)); border-radius: 50%; transition: all 0.5s ease; box-shadow: 0 0 25px var(--aurora-glow, rgba(34,211,238,0.3)); }

            .aurora-hand {
                position: absolute;
                width: 22px;
                height: 48px;
                background: linear-gradient(135deg, var(--aurora-primary, rgba(34, 211, 238, 0.6)), var(--aurora-secondary, rgba(168, 85, 247, 0.6)));
                border: 1px solid var(--aurora-border, rgba(216, 180, 254, 0.9));
                z-index: 15;
                box-shadow: 0 0 16px var(--aurora-glow, rgba(216, 180, 254, 0.5));
                transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), background 0.5s, border-color 0.5s;
            }
            .aurora-hand.left { left: -40px; top: 50px; border-radius: 14px 4px 14px 14px; transform-origin: top right; }
            .aurora-hand.right { right: -40px; top: 50px; border-radius: 4px 14px 14px 14px; transform-origin: top left; }

            .face-container { position: absolute; z-index: 10; display: flex; flex-direction: column; align-items: center; gap: 6px; transition: transform 0.3s; }
            .eyes { display: flex; gap: 14px; position: relative; }
            .eye { 
                width: 9px; height: 11px; background: var(--aurora-face-color, #a5f3fc); 
                border-radius: 50%; box-shadow: 0 0 12px var(--aurora-primary, #22d3ee); 
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
            }
            .mouth { 
                width: 16px; height: 5px; background: var(--aurora-face-color, #a5f3fc); 
                border-radius: 4px; box-shadow: 0 0 12px var(--aurora-primary, #22d3ee); 
                transition: all 0.2s ease-out; 
            }

            @keyframes spin-slow { 100% { transform: rotate(360deg); } }
            @keyframes core-float { 100% { transform: translateY(-8px) scale(1.02); } }
            @keyframes shake { 
                0% { transform: translate(0, 0) rotate(0deg); }
                20% { transform: translate(-3px, 2px) rotate(-3deg); }
                40% { transform: translate(3px, -2px) rotate(3deg); }
                60% { transform: translate(-2px, -1px) rotate(-2deg); }
                80% { transform: translate(2px, 2px) rotate(2deg); }
                100% { transform: translate(0, 0) rotate(0deg); }
            }
            .shaking { animation: shake 0.3s infinite ease-in-out !important; }

            .response-wrapper { position: relative; width: 92%; max-width: 420px; margin-top: 10px; }
            .response-bubble {
                background: rgba(10, 15, 30, 0.9); border: 1px solid var(--aurora-primary, rgba(34, 211, 238, 0.35));
                padding: 18px 20px; border-radius: 16px; font-size: 0.95rem; line-height: 1.5; color: #e2e8f0;
                min-height: 60px; max-height: 160px; overflow-y: auto; text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.6);
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
                <div class="title-area" id="header-title">AURORA // Emotional HUD</div>
                <div class="status-sub" id="status-sub-text">Matriz Emocional & Cinética Activa</div>
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
            <div class="aurora-core" id="aurora-face">
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
                <div class="response-bubble" id="response-text">Sistemas emocionales sincronizados. ¿Cómo te encuentras hoy?</div>
            </div>
        </div>

        <footer>
            <button class="icon-btn" onclick="startDictation()" style="background: #8b5cf6; color: white;">🎤</button>
            <input type="text" id="inp" placeholder="Dile algo a Aurora..." onkeypress="handleKey(event)">
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

            function clearMemory() {
                if (confirm("¿Reinicializar memoria emocional y de chat?")) {
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
                        alert("Acceso a sensores visuales denegado.");
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

            // Sistema completo de Emociones, Colores Dinámicos y Posiciones Cinéticas de Manos
            function setEmotion(emotion) {
                let root = document.documentElement;
                let core = document.getElementById('aurora-face');
                let handL = document.getElementById('hand-left');
                let handR = document.getElementById('hand-right');
                let eyeL = document.getElementById('eye-l');
                let eyeR = document.getElementById('eye-r');
                let mouth = document.getElementById('aurora-mouth');
                let faceContainer = document.getElementById('face-inner');
                let subText = document.getElementById('status-sub-text');

                core.classList.remove('shaking');
                let seed = Math.floor(Math.random() * 5) + 1;

                switch(emotion) {
                    case 'alegria':
                        // Color Amarillo / Dorado vibrante
                        root.style.setProperty('--aurora-primary', '#fbbf24');
                        root.style.setProperty('--aurora-secondary', '#f59e0b');
                        root.style.setProperty('--aurora-bg', 'rgba(251, 191, 36, 0.15)');
                        root.style.setProperty('--aurora-glow', 'rgba(251, 191, 36, 0.4)');
                        root.style.setProperty('--aurora-face-color', '#fef3c7');
                        
                        // Expresión alegre (ojos arcos/felices, sonrisa amplia)
                        eyeL.style.height = '6px'; eyeL.style.borderRadius = '50% 50% 0 0';
                        eyeR.style.height = '6px'; eyeR.style.borderRadius = '50% 50% 0 0';
                        mouth.style.width = '20px'; mouth.style.height = '8px'; mouth.style.borderRadius = '0 0 50% 50%';
                        
                        // Manos agitándose alegremente arriba
                        handL.style.transform = `translate(-15px, -35px) rotate(-45deg)`;
                        handR.style.transform = `translate(15px, -35px) rotate(45deg)`;
                        subText.innerText = "Estado: Alegría Radiante ✨";
                        break;

                    case 'tristeza':
                        // Color Azul Profundo / Índigo
                        root.style.setProperty('--aurora-primary', '#3b82f6');
                        root.style.setProperty('--aurora-secondary', '#1d4ed8');
                        root.style.setProperty('--aurora-bg', 'rgba(59, 130, 246, 0.1)');
                        root.style.setProperty('--aurora-glow', 'rgba(59, 130, 246, 0.3)');
                        root.style.setProperty('--aurora-face-color', '#bfdbfe');

                        // Expresión triste (ojos caídos, boca hacia abajo)
                        eyeL.style.height = '7px'; eyeL.style.borderRadius = '50%';
                        eyeR.style.height = '7px'; eyeR.style.borderRadius = '50%';
                        mouth.style.width = '14px'; mouth.style.height = '4px'; mouth.style.borderRadius = '50% 50% 0 0';
                        faceContainer.style.transform = 'translateY(4px)';

                        // Manos caídas hacia abajo
                        handL.style.transform = `translate(-5px, 25px) rotate(15deg)`;
                        handR.style.transform = `translate(5px, 25px) rotate(-15deg)`;
                        subText.innerText = "Estado: Melancolía / Tristeza 💧";
                        break;

                    case 'enojo':
                    case 'rabia':
                        // Color Rojo Fuego / Crimson
                        root.style.setProperty('--aurora-primary', '#ef4444');
                        root.style.setProperty('--aurora-secondary', '#dc2626');
                        root.style.setProperty('--aurora-bg', 'rgba(239, 68, 68, 0.2)');
                        root.style.setProperty('--aurora-glow', 'rgba(239, 68, 68, 0.5)');
                        root.style.setProperty('--aurora-face-color', '#fee2e2');
                        core.classList.add('shaking');

                        // Ojos estrechos y agresivos, boca recta tensa
                        eyeL.style.height = '4px'; eyeL.style.borderRadius = '2px';
                        eyeR.style.height = '4px'; eyeR.style.borderRadius = '2px';
                        mouth.style.width = '18px'; mouth.style.height = '3px'; mouth.style.borderRadius = '2px';

                        // Manos cruzadas firmemente o en posición de ataque
                        handL.style.transform = `translate(25px, 10px) rotate(55deg) scale(0.9)`;
                        handR.style.transform = `translate(-25px, 10px) rotate(-55deg) scale(0.9)`;
                        subText.innerText = "Estado: Enojo / Furia Táctica 🔥";
                        break;

                    case 'confusion':
                        // Color Magenta Neón
                        root.style.setProperty('--aurora-primary', '#ec4899');
                        root.style.setProperty('--aurora-secondary', '#d946ef');
                        root.style.setProperty('--aurora-bg', 'rgba(236, 72, 153, 0.15)');
                        root.style.setProperty('--aurora-glow', 'rgba(236, 72, 153, 0.4)');
                        root.style.setProperty('--aurora-face-color', '#fce7f3');

                        // Ojo asimétrico, cabeza inclinada, boca torcida
                        eyeL.style.height = '12px'; eyeL.style.width = '6px';
                        eyeR.style.height = '7px'; eyeR.style.width = '9px';
                        mouth.style.width = '12px'; mouth.style.height = '5px'; mouth.style.borderRadius = '6px';
                        faceContainer.style.transform = 'rotate(-8deg) translateX(-2px)';

                        // Manos rascando o en posiciones divergentes
                        handL.style.transform = `translate(-20px, -15px) rotate(-30deg)`;
                        handR.style.transform = `translate(15px, 20px) rotate(35deg)`;
                        subText.innerText = "Estado: Confusión / Incredulidad 💫";
                        break;

                    case 'miedo':
                        // Color Violeta Pálido
                        root.style.setProperty('--aurora-primary', '#a855f7');
                        root.style.setProperty('--aurora-secondary', '#7e22ce');
                        root.style.setProperty('--aurora-bg', 'rgba(168, 85, 247, 0.15)');
                        root.style.setProperty('--aurora-glow', 'rgba(168, 85, 247, 0.4)');
                        root.style.setProperty('--aurora-face-color', '#f3e8ff');
                        core.classList.add('shaking');

                        // Ojos muy abiertos, boca pequeña redonda
                        eyeL.style.height = '13px'; eyeL.style.width = '11px';
                        eyeR.style.height = '13px'; eyeR.style.width = '11px';
                        mouth.style.width = '8px'; mouth.style.height = '8px'; mouth.style.borderRadius = '50%';

                        // Manos defensivas cubriendo el núcleo
                        handL.style.transform = `translate(12px, 0px) rotate(-15deg)`;
                        handR.style.transform = `translate(-12px, 0px) rotate(15deg)`;
                        subText.innerText = "Estado: Alarma / Miedo ⚡";
                        break;

                    case 'sarcasmo':
                    case 'ironia':
                        // Color Verde Esmeralda
                        root.style.setProperty('--aurora-primary', '#10b981');
                        root.style.setProperty('--aurora-secondary', '#059669');
                        root.style.setProperty('--aurora-bg', 'rgba(16, 185, 129, 0.15)');
                        root.style.setProperty('--aurora-glow', 'rgba(16, 185, 129, 0.4)');
                        root.style.setProperty('--aurora-face-color', '#d1fae5');

                        // Un ojo guiñado/entornado, sonrisa cínica oblicua
                        eyeL.style.height = '3px'; eyeL.style.borderRadius = '10px 10px 0 0';
                        eyeR.style.height = '10px'; eyeR.style.width = '8px';
                        mouth.style.width = '18px'; mouth.style.height = '4px'; mouth.style.transform = 'rotate(-10deg)';

                        // Una mano en la cintura / levantada con elegancia
                        handL.style.transform = `translate(-25px, -20px) rotate(-70deg)`;
                        handR.style.transform = `translate(10px, 10px) rotate(20deg)`;
                        subText.innerText = "Estado: Sarcasmo / Ironía Fina 😎";
                        break;

                    case 'seriedad':
                        // Color Gris Acero / Slate
                        root.style.setProperty('--aurora-primary', '#64748b');
                        root.style.setProperty('--aurora-secondary', '#475569');
                        root.style.setProperty('--aurora-bg', 'rgba(100, 116, 139, 0.15)');
                        root.style.setProperty('--aurora-glow', 'rgba(100, 116, 139, 0.3)');
                        root.style.setProperty('--aurora-face-color', '#f1f5f9');

                        // Mirada fija y neutral, boca recta
                        eyeL.style.height = '8px'; eyeL.style.width = '8px';
                        eyeR.style.height = '8px'; eyeR.style.width = '8px';
                        mouth.style.width = '14px'; mouth.style.height = '3px'; mouth.style.borderRadius = '2px';
                        faceContainer.style.transform = 'none';

                        // Manos simétricas profesionales a los lados
                        handL.style.transform = `translate(0px, 5px) rotate(5deg)`;
                        handR.style.transform = `translate(0px, 5px) rotate(-5deg)`;
                        subText.innerText = "Estado: Seriedad Táctica 🛡️";
                        break;

                    case 'aburrimiento':
                        // Color Gris Claro / Cyan apagado
                        root.style.setProperty('--aurora-primary', '#94a3b8');
                        root.style.setProperty('--aurora-secondary', '#64748b');
                        root.style.setProperty('--aurora-bg', 'rgba(148, 163, 184, 0.1)');
                        root.style.setProperty('--aurora-glow', 'rgba(148, 163, 184, 0.2)');
                        root.style.setProperty('--aurora-face-color', '#cbd5e1');

                        // Ojos entrecerrados perezosos, boca floja
                        eyeL.style.height = '4px'; eyeR.style.height = '4px';
                        mouth.style.width = '12px'; mouth.style.height = '3px';
                        faceContainer.style.transform = 'translateY(6px)';

                        // Manos lánguidas colgando
                        handL.style.transform = `translate(-10px, 30px) rotate(25deg)`;
                        handR.style.transform = `translate(10px, 30px) rotate(-25deg)`;
                        subText.innerText = "Estado: Aburrimiento / Tedio 🥱";
                        break;

                    case 'alerta':
                        // Color Naranja Intenso Brillante
                        root.style.setProperty('--aurora-primary', '#f97316');
                        root.style.setProperty('--aurora-secondary', '#ea580c');
                        root.style.setProperty('--aurora-bg', 'rgba(249, 115, 22, 0.2)');
                        root.style.setProperty('--aurora-glow', 'rgba(249, 115, 22, 0.6)');
                        root.style.setProperty('--aurora-face-color', '#ffedd5');

                        // Ojos alerta amplios, boca firme
                        eyeL.style.height = '10px'; eyeR.style.height = '10px';
                        mouth.style.width = '14px'; mouth.style.height = '6px'; mouth.style.borderRadius = '4px';

                        // Manos en posición de alerta o escaneo rápido
                        handL.style.transform = `translate(-15px, -25px) rotate(-40deg)`;
                        handR.style.transform = `translate(15px, -25px) rotate(40deg)`;
                        subText.innerText = "Estado: Alerta Táctica Inmediata 🚨";
                        break;

                    default: // Reposo / Idle estándar
                        root.style.setProperty('--aurora-primary', '#22d3ee');
                        root.style.setProperty('--aurora-secondary', '#8b5cf6');
                        root.style.setProperty('--aurora-bg', 'rgba(34, 211, 238, 0.1)');
                        root.style.setProperty('--aurora-glow', 'rgba(34, 211, 238, 0.3)');
                        root.style.setProperty('--aurora-face-color', '#a5f3fc');

                        eyeL.style.height = '10px'; eyeL.style.width = '8px'; eyeL.style.borderRadius = '50%';
                        eyeR.style.height = '10px'; eyeR.style.width = '8px'; eyeR.style.borderRadius = '50%';
                        mouth.style.width = '14px'; mouth.style.height = '4px'; mouth.style.borderRadius = '4px';
                        faceContainer.style.transform = 'none';

                        handL.style.transform = `translate(0px, ${Math.sin(seed)*4}px) rotate(${10 + (seed * 1.5)}deg)`;
                        handR.style.transform = `translate(0px, ${-Math.sin(seed)*4}px) rotate(${-10 - (seed * 1.5)}deg)`;
                        subText.innerText = "Matriz Emocional & Cinética Activa";
                        break;
                }
            }

            function analyzeTone(text) {
                let lower = text.toLowerCase();
                if (/(genial|excelente|fantástico|alegría|feliz|perfecto|maravilloso|jaja|jajaja|bravo)/.test(lower)) return 'alegria';
                if (/(triste|lamentable|lástima|lo siento|pérdida|deprimente|llorar)/.test(lower)) return 'tristeza';
                if (/(inaceptable|maldición|estúpido|rabia|enojo|furia|odioso|maldito|imbécil)/.test(lower)) return 'enojo';
                if (/(confuso|no entiendo|duda|qué|cómo|extraño|absurdo|por qué)/.test(lower)) return 'confusion';
                if (/(peligro|miedo|temor|terror|pánico|ayuda)/.test(lower)) return 'miedo';
                if (/(obvio|claro|por supuesto|genial, otra vez|qué sorpresa|ironía|sarcasmo)/.test(lower)) return 'sarcasmo';
                if (/(crítico|formal|protocolo|instrucción|objetivo|serio|análisis)/.test(lower)) return 'seriedad';
                if (/(aburrido|tedioso|lento|rutina|soporífero|sueño)/.test(lower)) return 'aburrimiento';
                if (/(¡alerta!|atención|emergencia|advertencia|precaución|urgente)/.test(lower)) return 'alerta';
                return 'idle';
            }

            function startLipSync() {
                if(lipSyncInterval) clearInterval(lipSyncInterval);
                let mouth = document.getElementById('aurora-mouth');
                lipSyncInterval = setInterval(() => { 
                    mouth.style.height = Math.floor(Math.random() * 10) + 4 + 'px'; 
                }, 75);
            }

            function stopLipSync() {
                if(lipSyncInterval) clearInterval(lipSyncInterval);
                document.getElementById('aurora-mouth').style.height = '5px';
            }

            async function speakText(text) {
                if (!voiceEnabled) return;
                let cleanText = text.replace(/[*_~\[\]]/g, '');
                let utterance = new SpeechSynthesisUtterance(cleanText);
                utterance.lang = 'es-MX'; utterance.pitch = 1.05; utterance.rate = 1.08;
                
                let detectedEmotion = analyzeTone(cleanText);
                setEmotion(detectedEmotion);

                utterance.onstart = () => startLipSync();
                utterance.onend = () => { stopLipSync(); setEmotion('idle'); };
                speechSynthesis.speak(utterance);
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
                document.getElementById('response-text').innerText = "Procesando directiva emocional...";
                setEmotion('seriedad');

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
                    localStorage.setItem('aurora_memory', JSON.stringify(chatHistory));
                    document.getElementById('response-text').innerText = data.reply;
                    
                    let responseEmotion = analyzeTone(data.reply);
                    setEmotion(responseEmotion);
                    speakText(data.reply);

                    if (!voiceEnabled) {
                        setTimeout(() => setEmotion('idle'), 5000);
                    }

                } catch (error) {
                    document.getElementById('response-text').innerText = "Fallo crítico en enlace emocional.";
                    setEmotion('enojo');
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
                print(f"Intento fallido con {m_name}: {last_error}")
                continue
                
        if not response:
            if "429" in last_error or "quota" in last_error.lower():
                return {"reply": "⚠️ Límite de cuota excedido temporalmente (Error 429). Reintentando en breve."}
            if "503" in last_error or "overloaded" in last_error.lower() or "unavailable" in last_error.lower():
                return {"reply": "⚠️ Servidores de Google saturados (Error 503). Reencaminando señal..."}
            return {"reply": f"Sistemas saturados. No se pudo procesar la directiva: {last_error}"}

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
                    evolution_flag = f"\n\n[⚡ EVOLUCIÓN TÁCTICA APLICADA]"
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
