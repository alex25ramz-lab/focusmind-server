from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import os

app = Flask(__name__)

# Base de datos en memoria (Se reinicia al apagar el servidor en Render)
db = {
    "tarea_actual": "Esperando mando...",
    "tiempo_actual": 0,
    "id_envio": 0,
    "historial": [],
    "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0}
}

# --- INTERFAZ NEÓN CON AUTO-REFRESH ---
HTML_PANEL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind OS Hub</title>
    <style>
        :root { --neon: #00ffaa; --bg: #050505; --card: #0d0d0d; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: white; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: auto; }
        h1 { color: var(--neon); text-align: center; font-size: 28px; text-shadow: 0 0 15px var(--neon); letter-spacing: 3px; margin-bottom: 30px; }
        .card { background: var(--card); border: 2px solid #1a1a1a; border-radius: 20px; padding: 25px; margin-bottom: 25px; }
        label { display: block; margin-bottom: 10px; color: var(--neon); font-size: 11px; font-weight: bold; text-transform: uppercase; }
        input { width: 100%; padding: 15px; margin-bottom: 20px; border-radius: 10px; border: 1px solid #333; background: #000; color: white; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 18px; border-radius: 12px; border: none; background: var(--neon); color: black; font-weight: 900; font-size: 16px; cursor: pointer; box-shadow: 0 0 15px var(--neon); }
        .stats { display: flex; justify-content: space-between; text-align: center; }
        .stat-num { display: block; font-size: 30px; font-weight: bold; color: var(--neon); }
        .stat-label { font-size: 10px; color: #555; text-transform: uppercase; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        td { padding: 15px 5px; border-bottom: 1px solid #1a1a1a; }
        .badge { padding: 5px 10px; border-radius: 6px; font-size: 10px; font-weight: bold; text-transform: uppercase; border: 1px solid transparent; }
        .hecho { border-color: var(--neon); color: var(--neon); background: rgba(0, 255, 170, 0.1); }
        .retraso { border-color: #ff4444; color: #ff4444; background: rgba(255, 68, 68, 0.1); }
        .pendiente { border-color: #555; color: #555; }
    </style>
</head>
<body>
    <div class="container">
        <h1>FOCUSMIND OS</h1>
        <div class="card">
            <form action="/enviar_tarea_web" method="POST">
                <label>¿Qué tienes pensado hoy?</label>
                <input type="text" name="tarea" placeholder="Escribe el objetivo..." required>
                <label>Tiempo de enfoque (Minutos)</label>
                <input type="number" name="mins" placeholder="Ej. 45" required>
                <button type="submit">Desplegar Objetivo</button>
            </form>
        </div>
        <div class="card">
            <div class="stats">
                <div class="stat-box"><span class="stat-num">{{ rendimiento.total }}</span><span class="stat-label">Total</span></div>
                <div class="stat-box"><span class="stat-num">{{ rendimiento.exitos }}</span><span class="stat-label">Éxitos</span></div>
                <div class="stat-box" style="color:#ff4444;"><span class="stat-num" style="color:#ff4444;">{{ rendimiento.retrasos }}</span><span class="stat-label">Retrasos / Exp</span></div>
            </div>
        </div>
        <div class="card">
            <label>Registro de Operaciones</label>
            <table>
                {% for item in historial[::-1][:8] %}
                <tr>
                    <td>
                        <div style="color:#eee; font-weight:bold; font-size:14px;">{{ item.tarea }}</div>
                        <div style="color:#444; font-size:11px;">{{ item.hora }}</div>
                    </td>
                    <td style="text-align:right;">
                        <span class="badge {{ 'hecho' if item.estado == 'HECHO' else 'retraso' if item.estado in ['RETARDO', 'EXPIRADA'] else 'pendiente' }}">
                            {{ item.estado }}
                        </span>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <script>
        // Monitoreo de cambios para refrescar la UI automáticamente
        let hashEstado = "{{ historial|length }}-{{ rendimiento.exitos }}-{{ rendimiento.retrasos }}";
        setInterval(async () => {
            try {
                const res = await fetch('/verificar_cambios');
                const data = await res.json();
                if (data.hash != hashEstado) {
                    window.location.reload();
                }
            } catch (e) {}
        }, 3000);
    </script>
</body>
</html>
"""

# --- RUTAS DE LA API ---

@app.route('/')
def home():
    return render_template_string(HTML_PANEL, historial=db['historial'], rendimiento=db['rendimiento'])

@app.route('/verificar_cambios')
def verificar_cambios():
    # Creamos un hash simple para saber si algo cambió en la DB
    hash_actual = f"{len(db['historial'])}-{db['rendimiento']['exitos']}-{db['rendimiento']['retrasos']}"
    return jsonify({"hash": hash_actual})

@app.route('/enviar_tarea_web', methods=['POST'])
def enviar_tarea_web():
    tarea = request.form.get('tarea')
    mins = request.form.get('mins')
    db['id_envio'] += 1
    db['tarea_actual'], db['tiempo_actual'] = tarea, mins
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
    """Ruta que consulta la App FocusMind (Python local)"""
    return jsonify({
        "tarea": db['tarea_actual'], 
        "tiempo": db['tiempo_actual'], 
        "id": db['id_envio']
    })

@app.route('/reportar_progreso', methods=['POST'])
def reportar_progreso():
    """Ruta donde la App reporta el resultado final"""
    data = request.json
    id_tarea = data.get('id')
    nuevo_estado = data.get('estado') # Esperamos: 'HECHO', 'RETARDO' o 'EXPIRADA'
    
    for t in db['historial']:
        if t['id'] == id_tarea:
            if t['estado'] == "PENDIENTE":
                t['estado'] = nuevo_estado
                # Lógica corregida de contadores
                if nuevo_estado == "HECHO":
                    db['rendimiento']['exitos'] += 1
                elif nuevo_estado in ["RETARDO", "EXPIRADA"]:
                    db['rendimiento']['retrasos'] += 1
            break
    return jsonify({"status": "OK"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
