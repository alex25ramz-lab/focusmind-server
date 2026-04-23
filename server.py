from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import os
import random

app = Flask(__name__)

# Base de datos en memoria
db = {
    "tarea_actual": "Esperando mando...",
    "tiempo_actual": 0,
    "id_envio": 0,
    "historial": [],
    "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0},
    "ultimo_msj": "Sistemas AXON en línea. Esperando directivas."
}

# --- PROTOCOLOS DE COMUNICACIÓN AXON ---
FRASES_ENTRADA = [
    "Objetivo recibido. Optimizando recursos para la ejecución.",
    "Protocolo de enfoque activado. Iniciando secuencia.",
    "Analizando complejidad... Sistemas listos para el despliegue.",
    "Temporizador sincronizado. Sin distracciones, adelante.",
    "Iniciando secuencia de ejecución. El éxito es la única variable.",
    "Objetivo fijado en el radar. Mantén el flujo constante."
]

HTML_PANEL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AXON OS - Interface</title>
    <style>
        :root { --neon: #00ffaa; --bg: #050505; --card: #0d0d0d; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: white; margin: 0; padding: 20px; overflow-x: hidden; }
        .container { max-width: 500px; margin: auto; }
        h1 { color: var(--neon); text-align: center; font-size: 28px; text-shadow: 0 0 15px var(--neon); letter-spacing: 5px; margin-bottom: 20px; }
        
        .axon-console { 
            background: rgba(0, 255, 170, 0.03); 
            border-left: 3px solid var(--neon); 
            padding: 15px; 
            margin-bottom: 25px; 
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: var(--neon);
            position: relative;
        }
        
        .typing { overflow: hidden; white-space: nowrap; border-right: 2px solid var(--neon); animation: typing 3s steps(40, end), blink .75s step-end infinite; }
        @keyframes typing { from { width: 0 } to { width: 100% } }
        @keyframes blink { from, to { border-color: transparent } 50% { border-color: var(--neon); } }

        .card { background: var(--card); border: 2px solid #1a1a1a; border-radius: 20px; padding: 25px; margin-bottom: 25px; }
        label { display: block; margin-bottom: 10px; color: var(--neon); font-size: 11px; font-weight: bold; text-transform: uppercase; }
        input { width: 100%; padding: 15px; margin-bottom: 20px; border-radius: 10px; border: 1px solid #333; background: #000; color: white; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 18px; border-radius: 12px; border: none; background: var(--neon); color: black; font-weight: 900; font-size: 16px; cursor: pointer; box-shadow: 0 0 15px var(--neon); transition: 0.3s; }
        
        .stats { display: flex; justify-content: space-between; text-align: center; }
        .stat-num { display: block; font-size: 30px; font-weight: bold; color: var(--neon); }
        .stat-label { font-size: 10px; color: #555; text-transform: uppercase; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        td { padding: 15px 5px; border-bottom: 1px solid #1a1a1a; }
        .badge { padding: 5px 10px; border-radius: 6px; font-size: 10px; font-weight: bold; text-transform: uppercase; border: 1px solid transparent; }
        .hecho { border-color: var(--neon); color: var(--neon); background: rgba(0, 255, 170, 0.1); }
        .retraso { border-color: #666; color: #999; background: rgba(255, 255, 255, 0.05); }
    </style>
</head>
<body>
    <div class="container">
        <h1>AXON OS</h1>

        <div class="axon-console">
            <div id="msj-texto" class="typing">> AXON: {{ ultimo_msj }}</div>
        </div>

        <div class="card">
            <form action="/enviar_tarea_web" method="POST">
                <label>Nuevo Objetivo de Ingeniería</label>
                <input type="text" name="tarea" placeholder="Definir meta..." required>
                <label>Tiempo (Mins)</label>
                <input type="number" name="mins" placeholder="45" required>
                <button type="submit">DESPLEGAR AXON</button>
            </form>
        </div>

        <div class="card stats">
            <div class="stat-box"><span class="stat-num">{{ rendimiento.total }}</span><span class="stat-label">Total</span></div>
            <div class="stat-box"><span class="stat-num">{{ rendimiento.exitos }}</span><span class="stat-label">Éxitos</span></div>
            <div class="stat-box"><span class="stat-num" style="color:#ff4444;">{{ rendimiento.retrasos }}</span><span class="stat-label">Retrasos</span></div>
        </div>

        <div class="card">
            <label>Log de Operaciones</label>
            <table>
                {% for item in historial[::-1][:5] %}
                <tr>
                    <td><div style="color:#eee; font-weight:bold;">{{ item.tarea }}</div></td>
                    <td style="text-align:right;">
                        <span class="badge {{ 'hecho' if item.estado == 'HECHO' else 'retraso' if 'RETARDO' in item.estado or 'EXPIRADA' in item.estado else '' }}">
                            {{ item.estado }}
                        </span>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <script>
        // --- FUNCIÓN DE VOZ ---
        function hablar(texto) {
            if ('speechSynthesis' in window) {
                const mensaje = new SpeechSynthesisUtterance(texto.replace("> AXON:", ""));
                mensaje.lang = 'es-MX';
                mensaje.rate = 0.9; // Velocidad un poco más lenta para que suene serio
                mensaje.pitch = 0.8; // Tono un poco más grave
                window.speechSynthesis.speak(mensaje);
            }
        }

        // Ejecutar voz al cargar si el mensaje cambió
        window.onload = () => {
            const textoActual = document.getElementById('msj-texto').innerText;
            hablar(textoActual);
        };

        // --- REFRESH AUTOMÁTICO ---
        let hashEstado = "{{ historial|length }}-{{ rendimiento.exitos }}-{{ rendimiento.retrasos }}";
        setInterval(async () => {
            try {
                const res = await fetch('/verificar_cambios');
                const data = await res.json();
                if (data.hash != hashEstado) window.location.reload();
            } catch (e) {}
        }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PANEL, historial=db['historial'], rendimiento=db['rendimiento'], ultimo_msj=db['ultimo_msj'])

@app.route('/verificar_cambios')
def verificar_cambios():
    hash_actual = f"{len(db['historial'])}-{db['rendimiento']['exitos']}-{db['rendimiento']['retrasos']}"
    return jsonify({"hash": hash_actual})

@app.route('/enviar_tarea_web', methods=['POST'])
def enviar_tarea_web():
    tarea, mins = request.form.get('tarea'), request.form.get('mins')
    db['id_envio'] += 1
    db['tarea_actual'], db['tiempo_actual'] = tarea, mins
    db['ultimo_msj'] = random.choice(FRASES_ENTRADA)
    db['historial'].append({"id": db['id_envio'], "tarea": tarea, "estado": "PENDIENTE", "hora": datetime.now().strftime("%H:%M")})
    db['rendimiento']['total'] += 1
    return '<script>window.location.href="/";</script>'

@app.route('/get_data')
def get_data():
    return jsonify({"tarea": db['tarea_actual'], "tiempo": db['tiempo_actual'], "id": db['id_envio']})

@app.route('/reportar_progreso', methods=['POST'])
def reportar_progreso():
    data = request.json
    id_tarea, nuevo_estado = data.get('id'), data.get('estado').upper()
    for t in db['historial']:
        if t['id'] == id_tarea and t['estado'] == "PENDIENTE":
            t['estado'] = nuevo_estado
            if nuevo_estado == "HECHO":
                db['rendimiento']['exitos'] += 1
                db['ultimo_msj'] = "Objetivo completado con éxito. Excelente trabajo."
            elif any(x in nuevo_estado for x in ["RETARDO", "EXPIRADA", "RETRASO"]):
                db['rendimiento']['retrasos'] += 1
                db['ultimo_msj'] = "Alerta. Se ha detectado una desviación en el tiempo de entrega."
            break
    return jsonify({"status": "OK"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
