from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import os
import random

app = Flask(__name__)

db = {
    "tarea_actual": "Esperando mando...",
    "tiempo_actual": 0,
    "id_envio": 0,
    "historial": [],
    "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0},
    "ultimo_msj": "Sistemas LUMINA iniciados. Esperando enlace."
}

FRASES_LUMINA = [
    "Objetivo detectado. Optimizando frecuencia de enfoque.",
    "Lumina en línea. Iniciando secuencia de productividad.",
    "Sistemas listos. La disciplina es el puente al éxito.",
    "Temporizador anclado. No se detectan errores en el plan.",
    "Procesando nueva meta. Ejecución prioritaria activada.",
    "Enfoque de ingeniería establecido. Adelante."
]

HTML_PANEL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LUMINA OS - Interface</title>
    <style>
        :root { --neon: #00ffaa; --bg: #050505; --card: #0d0d0d; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: white; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: auto; }
        h1 { color: var(--neon); text-align: center; font-size: 28px; text-shadow: 0 0 15px var(--neon); letter-spacing: 5px; }
        
        .console { 
            background: rgba(0, 255, 170, 0.03); 
            border-left: 3px solid var(--neon); 
            padding: 15px; margin-bottom: 20px; 
            font-family: 'Courier New', monospace; font-size: 13px; color: var(--neon);
        }

        .audio-status {
            text-align: center; margin-bottom: 15px;
        }

        .audio-btn {
            background: rgba(0, 255, 170, 0.1); border: 1px solid var(--neon); color: var(--neon);
            padding: 8px; font-size: 10px; cursor: pointer; border-radius: 8px; width: 100%;
            font-weight: bold; text-transform: uppercase;
        }

        .card { background: var(--card); border: 2px solid #1a1a1a; border-radius: 20px; padding: 25px; margin-bottom: 25px; }
        label { display: block; margin-bottom: 10px; color: var(--neon); font-size: 11px; font-weight: bold; text-transform: uppercase; }
        input { width: 100%; padding: 15px; margin-bottom: 20px; border-radius: 10px; border: 1px solid #333; background: #000; color: white; box-sizing: border-box; outline: none; }
        button.main-btn { width: 100%; padding: 18px; border-radius: 12px; border: none; background: var(--neon); color: black; font-weight: 900; font-size: 16px; cursor: pointer; box-shadow: 0 0 15px var(--neon); }
        
        .stats { display: flex; justify-content: space-between; text-align: center; }
        .stat-num { display: block; font-size: 30px; font-weight: bold; color: var(--neon); }
        .stat-label { font-size: 10px; color: #555; text-transform: uppercase; }

        /* TABLA DE REGISTRO */
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        td { padding: 12px 5px; border-bottom: 1px solid #1a1a1a; font-size: 14px; }
        .badge { padding: 4px 8px; border-radius: 5px; font-size: 9px; font-weight: bold; text-transform: uppercase; border: 1px solid; }
        .hecho { border-color: var(--neon); color: var(--neon); }
        .retraso { border-color: #ff4444; color: #ff4444; }
        .pendiente { border-color: #444; color: #444; }
    </style>
</head>
<body>
    <div class="container">
        <h1>LUMINA OS</h1>
        
        <div class="audio-status" id="audio-container">
            <button class="audio-btn" onclick="permitirVoz()">Sincronizar Voz de Lumina</button>
        </div>

        <div class="console">
            <div id="msj-texto">> LUMINA: {{ ultimo_msj }}</div>
        </div>

        <div class="card">
            <form action="/enviar_tarea_web" method="POST">
                <label>Desplegar Objetivo</label>
                <input type="text" name="tarea" placeholder="¿Qué vamos a lograr?" required>
                <label>Tiempo Estimado (Mins)</label>
                <input type="number" name="mins" placeholder="Ej. 45" required>
                <button type="submit" class="main-btn">INICIAR SECUENCIA</button>
            </form>
        </div>

        <div class="card stats">
            <div class="stat-box"><span class="stat-num">{{ rendimiento.total }}</span><span class="stat-label">Total</span></div>
            <div class="stat-box"><span class="stat-num">{{ rendimiento.exitos }}</span><span class="stat-label">Éxitos</span></div>
            <div class="stat-box"><span class="stat-num" style="color:#ff4444;">{{ rendimiento.retrasos }}</span><span class="stat-label">Retrasos</span></div>
        </div>

        <div class="card">
            <label>Registro de Operaciones</label>
            <table>
                {% for item in historial[::-1][:5] %}
                <tr>
                    <td>
                        <div style="font-weight:bold;">{{ item.tarea }}</div>
                        <div style="font-size:10px; color:#444;">ID: #{{ item.id }}</div>
                    </td>
                    <td style="text-align:right;">
                        <span class="badge {{ 'hecho' if item.estado == 'HECHO' else 'retraso' if 'RETARDO' in item.estado or 'RETRASO' in item.estado else 'pendiente' }}">
                            {{ item.estado }}
                        </span>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <script>
        // Lógica de Voz Persistente
        function permitirVoz() {
            sessionStorage.setItem('vozActivada', 'true');
            document.getElementById('audio-container').style.display = 'none';
            hablar("Sistemas de voz sincronizados y activos.");
        }

        function hablar(texto) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const msj = new SpeechSynthesisUtterance(texto.replace("> LUMINA:", ""));
                msj.lang = 'es-ES';
                msj.rate = 1.0;
                window.speechSynthesis.speak(msj);
            }
        }

        window.onload = () => {
            const texto = document.getElementById('msj-texto').innerText;
            if (sessionStorage.getItem('vozActivada') === 'true') {
                document.getElementById('audio-container').style.display = 'none';
                hablar(texto);
            }
        };

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
    db['ultimo_msj'] = random.choice(FRASES_LUMINA)
    db['historial'].append({"id": db['id_envio'], "tarea": tarea, "estado": "PENDIENTE"})
    db['rendimiento']['total'] += 1
    return '<script>window.location.href="/";</script>'

@app.route('/reportar_progreso', methods=['POST'])
def reportar_progreso():
    data = request.json
    id_t, estado = data.get('id'), data.get('estado').upper()
    for t in db['historial']:
        if t['id'] == id_t and t['estado'] == "PENDIENTE":
            t['estado'] = estado
            if estado == "HECHO":
                db['rendimiento']['exitos'] += 1
                db['ultimo_msj'] = "Objetivo completado. Rendimiento óptimo."
            else:
                db['rendimiento']['retrasos'] += 1
                db['ultimo_msj'] = "Alerta de retraso detectada en el sistema."
            break
    return jsonify({"status": "OK"})

@app.route('/get_data')
def get_data():
    return jsonify({"tarea": db['tarea_actual'], "tiempo": db['tiempo_actual'], "id": db['id_envio']})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
