from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import os
import random

app = Flask(__name__)

# Base de datos en memoria mejorada para Jarvis
db = {
    "tarea_actual": "Esperando mando...",
    "tiempo_actual": 0,
    "id_envio": 0,
    "historial": [],
    "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0},
    "ultimo_msj": "Sistemas en línea. Esperando directivas de ingeniería."
}

# --- PROTOCOLOS DE VOZ/TEXTO JARVIS ---
FRASES_ENTRADA = [
    "Objetivo recibido. La eficiencia es la única variable aceptable.",
    "Protocolo de enfoque iniciado. Optimizando recursos.",
    "Analizando complejidad del objetivo... Sistemas listos.",
    "Temporizador sincronizado. No se permiten distracciones.",
    "Iniciando secuencia de ejecución. Adelante, ingeniera.",
    "Objetivo fijado. Mantén el flujo de trabajo constante."
]

# --- INTERFAZ NEÓN JARVIS EDITION ---
HTML_PANEL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind OS - Jarvis Mode</title>
    <style>
        :root { --neon: #00ffaa; --bg: #050505; --card: #0d0d0d; }
        body { font-family: 'Segoe UI', 'Courier New', monospace; background: var(--bg); color: white; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: auto; }
        h1 { color: var(--neon); text-align: center; font-size: 28px; text-shadow: 0 0 15px var(--neon); letter-spacing: 3px; margin-bottom: 20px; }
        
        /* CONSOLA JARVIS */
        .jarvis-console { 
            background: rgba(0, 255, 170, 0.03); 
            border-left: 3px solid var(--neon); 
            padding: 15px; 
            margin-bottom: 25px; 
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: var(--neon);
        }
        .typing { overflow: hidden; white-space: nowrap; border-right: 2px solid var(--neon); animation: typing 3s steps(40, end), blink .75s step-end infinite; }
        @keyframes typing { from { width: 0 } to { width: 100% } }
        @keyframes blink { from, to { border-color: transparent } 50% { border-color: var(--neon); } }

        .card { background: var(--card); border: 2px solid #1a1a1a; border-radius: 20px; padding: 25px; margin-bottom: 25px; }
        label { display: block; margin-bottom: 10px; color: var(--neon); font-size: 11px; font-weight: bold; text-transform: uppercase; }
        input { width: 100%; padding: 15px; margin-bottom: 20px; border-radius: 10px; border: 1px solid #333; background: #000; color: white; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 18px; border-radius: 12px; border: none; background: var(--neon); color: black; font-weight: 900; font-size: 16px; cursor: pointer; box-shadow: 0 0 15px var(--neon); transition: 0.3s; }
        button:hover { transform: scale(1.02); }
        
        .stats { display: flex; justify-content: space-between; text-align: center; }
        .stat-num { display: block; font-size: 30px; font-weight: bold; color: var(--neon); }
        .stat-label { font-size: 10px; color: #555; text-transform: uppercase; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        td { padding: 15px 5px; border-bottom: 1px solid #1a1a1a; }
        .badge { padding: 5px 10px; border-radius: 6px; font-size: 10px; font-weight: bold; text-transform: uppercase; border: 1px solid transparent; }
        .hecho { border-color: var(--neon); color: var(--neon); background: rgba(0, 255, 170, 0.1); }
        .retraso { border-color: #666; color: #999; background: rgba(255, 255, 255, 0.05); }
        .pendiente { border-color: #333; color: #555; }
    </style>
</head>
<body>
    <div class="container">
        <h1>FOCUSMIND OS</h1>

        <div class="jarvis-console">
            <div class="typing">> JARVIS: {{ ultimo_msj }}</div>
        </div>

        <div class="card">
            <form action="/enviar_tarea_web" method="POST">
                <label>Definir nuevo objetivo de ingeniería</label>
                <input type="text" name="tarea" placeholder="Desplegar tarea..." required>
                <label>Tiempo de ejecución (Mins)</label>
                <input type="number" name="mins" placeholder="45" required>
                <button type="submit">INICIAR PROTOCOLO</button>
            </form>
        </div>

        <div class="card">
            <div class="stats">
                <div class="stat-box"><span class="stat-num">{{ rendimiento.total }}</span><span class="stat-label">Total</span></div>
                <div class="stat-box"><span class="stat-num">{{ rendimiento.exitos }}</span><span class="stat-label">Éxitos</span></div>
                <div class="stat-box"><span class="stat-num" style="color:#ff4444;">{{ rendimiento.retrasos }}</span><span class="stat-label">Retrasos / Exp</span></div>
            </div>
        </div>

        <div class="card">
            <label>Historial de Operaciones</label>
            <table>
                {% for item in historial[::-1][:5] %}
                <tr>
                    <td>
                        <div style="color:#eee; font-weight:bold; font-size:14px;">{{ item.tarea }}</div>
                        <div style="color:#444; font-size:11px;">{{ item.hora }}</div>
                    </td>
                    <td style="text-align:right;">
                        <span class="badge {{ 'hecho' if item.estado == 'HECHO' else 'retraso' if 'RETARDO' in item.estado or 'EXPIRADA' in item.estado else 'pendiente' }}">
                            {{ item.estado }}
                        </span>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <script>
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
    tarea = request.form.get('tarea')
    mins = request.form.get('mins')
    db['id_envio'] += 1
    db['tarea_actual'], db['tiempo_actual'] = tarea, mins
    
    # Jarvis responde al nuevo objetivo
    db['ultimo_msj'] = random.choice(FRASES_ENTRADA)
    
    db['historial'].append({
        "id": db['id_envio'], 
        "tarea": tarea, 
        "estado": "PENDIENTE", 
        "hora": datetime.now().strftime("%H:%M")
    })
    db['rendimiento']['total'] += 1
    return '<script>window.location.href="/";</script>'

@app.route('/get_data')
def get_data():
    return jsonify({"tarea": db['tarea_actual'], "tiempo": db['tiempo_actual'], "id": db['id_envio']})

@app.route('/reportar_progreso', methods=['POST'])
def reportar_progreso():
    data = request.json
    id_tarea = data.get('id')
    nuevo_estado = data.get('estado').upper()
    
    for t in db['historial']:
        if t['id'] == id_tarea and t['estado'] == "PENDIENTE":
            t['estado'] = nuevo_estado
            
            # --- Lógica de contadores CORREGIDA (Búsqueda flexible) ---
            if nuevo_estado == "HECHO":
                db['rendimiento']['exitos'] += 1
                db['ultimo_msj'] = "Excelente desempeño. Objetivo neutralizado."
            elif any(x in nuevo_estado for x in ["RETARDO", "EXPIRADA", "RETRASO"]):
                db['rendimiento']['retrasos'] += 1
                db['ultimo_msj'] = "Atención: Se ha registrado una demora en el protocolo."
            break
    return jsonify({"status": "OK"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
