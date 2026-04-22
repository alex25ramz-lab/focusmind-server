from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import os

app = Flask(__name__)

# --- BASE DE DATOS TEMPORAL (Se reinicia si el servidor se apaga) ---
db = {
    "tarea_actual": "Esperando asignación...",
    "tiempo_actual": 0,
    "id_envio": 0,
    "historial": [],
    "rendimiento": {
        "exitos": 0, 
        "retrasos": 0, 
        "total": 0
    }
}

# --- INTERFAZ PARA EL CELULAR (HTML/CSS) ---
HTML_PANEL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind OS Hub</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0a0a0a; color: white; margin: 0; padding: 20px; }
        .container { max-width: 500px; margin: auto; }
        h1 { color: #00ffaa; text-align: center; font-size: 26px; letter-spacing: 2px; text-shadow: 0 0 10px #00ffaa55; }
        .card { background: #121212; border: 1px solid #333; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        label { display: block; margin-bottom: 8px; color: #00ffaa; font-size: 12px; font-weight: bold; text-transform: uppercase; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #444; background: #1a1a1a; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 15px; border-radius: 8px; border: none; background: #00ffaa; color: black; font-weight: bold; font-size: 16px; cursor: pointer; transition: 0.3s; }
        button:active { transform: scale(0.98); background: #00cc88; }
        .stats { display: flex; justify-content: space-between; text-align: center; }
        .stat-box { flex: 1; }
        .stat-num { display: block; font-size: 24px; font-weight: bold; color: #00ffaa; }
        .stat-label { font-size: 10px; color: #666; text-transform: uppercase; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
        th { text-align: left; color: #444; border-bottom: 1px solid #333; padding: 8px; text-transform: uppercase; font-size: 10px; }
        td { padding: 12px 8px; border-bottom: 1px solid #1a1a1a; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; text-transform: uppercase; }
        .hecho { background: #00ffaa22; color: #00ffaa; }
        .retraso { background: #ff444422; color: #ff4444; }
        .pendiente { background: #333; color: #aaa; }
    </style>
</head>
<body>
    <div class="container">
        <h1>FOCUSMIND OS HUB</h1>
        
        <div class="card">
            <form action="/enviar_tarea_web" method="POST">
                <label>Misión / Tarea:</label>
                <input type="text" name="tarea" placeholder="Ej: Análisis de Circuitos" required>
                <label>Tiempo Estimado (Min):</label>
                <input type="number" name="mins" value="25" min="1" required>
                <button type="submit">DESPLEGAR A ESTACIÓN</button>
            </form>
        </div>

        <div class="card">
            <label style="text-align:center; margin-bottom:15px;">Rendimiento del Operador</label>
            <div class="stats">
                <div class="stat-box"><span class="stat-num">{{ rendimiento.total }}</span><span class="stat-label">Total</span></div>
                <div class="stat-box"><span class="stat-num" style="color:#00ffaa;">{{ rendimiento.exitos }}</span><span class="stat-label">Éxitos</span></div>
                <div class="stat-box"><span class="stat-num" style="color:#ff4444;">{{ rendimiento.retrasos }}</span><span class="stat-label">Retrasos</span></div>
            </div>
        </div>

        <div class="card">
            <label>Historial de Actividad</label>
            <table>
                <thead>
                    <tr><th>Tarea</th><th>Estado</th></tr>
                </thead>
                <tbody>
                    {% for item in historial[::-1][:8] %}
                    <tr>
                        <td>
                            <span style="color:#eee; font-weight:500;">{{ item.tarea }}</span><br>
                            <small style="color:#555;">{{ item.hora }}</small>
                        </td>
                        <td style="text-align:right;">
                            <span class="badge {{ 'hecho' if 'HECHO' in item.estado and 'RETRASO' not in item.estado else 'retraso' if 'RETRASO' in item.estado else 'pendiente' }}">
                                {{ item.estado }}
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

# --- RUTAS DEL SERVIDOR ---

@app.route('/')
def home():
    """Ruta principal para ver el panel en el celular."""
    return render_template_string(HTML_PANEL, historial=db['historial'], rendimiento=db['rendimiento'])

@app.route('/enviar_tarea_web', methods=['POST'])
def enviar_tarea_web():
    """Recibe datos desde el formulario del celular."""
    tarea = request.form.get('tarea')
    mins = request.form.get('mins')
    
    db['tarea_actual'] = tarea
    db['tiempo_actual'] = mins
    db['id_envio'] += 1
    
    db['historial'].append({
        "id": db['id_envio'],
        "tarea": tarea,
        "estado": "PENDIENTE",
        "hora": datetime.now().strftime("%H:%M")
    })
    db['rendimiento']['total'] += 1
    
    # Regresa a la página principal tras enviar
    return '<script>window.location.href="/";</script>'

@app.route('/get_data')
def get_data():
    """Ruta que consulta la Laptop (main.py) cada 5 segundos."""
    return jsonify({
        "tarea": db['tarea_actual'], 
        "tiempo": db['tiempo_actual'], 
        "id": db['id_envio']
    })

@app.route('/reportar_progreso', methods=['POST'])
def reportar_progreso():
    """Ruta donde la Laptop avisa si terminó la tarea y cómo."""
    data = request.json
    id_tarea = data.get('id')
    estado = data.get('estado') # Espera "HECHO" o "HECHO (CON RETRASO)"

    for t in db['historial']:
        if t['id'] == id_tarea:
            t['estado'] = estado
            if "RETRASO" in estado:
                db['rendimiento']['retrasos'] += 1
            else:
                db['rendimiento']['exitos'] += 1
            break
    return jsonify({"status": "actualizado"})

# --- INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    # Configuración específica para Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
