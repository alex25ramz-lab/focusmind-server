from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# BASE DE DATOS EN MEMORIA
db = {
    "tarea_actual": "Ninguna",
    "tiempo_actual": 0,
    "id_envio": 0,
    "historial": [],
    "rendimiento": {"exitos": 0, "retrasos": 0, "total": 0}
}

# DISEÑO VISUAL PARA EL CELULAR (HTML/CSS)
HTML_PANEL = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FocusMind OS Hub</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0a0a0a; color: white; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: auto; }
        h1 { color: #00ffaa; text-align: center; font-size: 24px; text-shadow: 0 0 10px #00ffaa55; }
        .card { background: #151515; border: 1px solid #333; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
        label { display: block; margin-bottom: 10px; color: #aaa; font-size: 14px; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #444; background: #222; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 15px; border-radius: 8px; border: none; background: #00ffaa; color: black; font-weight: bold; font-size: 16px; cursor: pointer; }
        .stats { display: flex; justify-content: space-between; text-align: center; }
        .stat-box { flex: 1; }
        .stat-num { display: block; font-size: 22px; font-weight: bold; color: #00ffaa; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { text-align: left; color: #666; border-bottom: 1px solid #333; padding: 8px; }
        td { padding: 10px 8px; border-bottom: 1px solid #222; }
        .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; }
        .hecho { background: #00ffaa22; color: #00ffaa; }
        .retraso { background: #ff444422; color: #ff4444; }
        .pendiente { background: #444; color: #eee; }
    </style>
</head>
<body>
    <div class="container">
        <h1>FOCUSMIND OS HUB</h1>
        
        <div class="card">
            <form action="/enviar_tarea_web" method="POST">
                <label>Nueva Tarea:</label>
                <input type="text" name="tarea" placeholder="Ej: Estudiar Dinámica" required>
                <label>Tiempo (minutos):</label>
                <input type="number" name="mins" value="25" required>
                <button type="submit">DESPLEGAR A LA ESTACIÓN</button>
            </form>
        </div>

        <div class="card">
            <div class="stats">
                <div class="stat-box"><span class="stat-num">{{ rendimiento.total }}</span><label>Total</label></div>
                <div class="stat-box"><span class="stat-num" style="color: #00ffaa;">{{ rendimiento.exitos }}</span><label>A tiempo</label></div>
                <div class="stat-box"><span class="stat-num" style="color: #ff4444;">{{ rendimiento.retrasos }}</span><label>Retrasos</label></div>
            </div>
        </div>

        <div class="card">
            <label>Historial Reciente</label>
            <table>
                <thead>
                    <tr><th>Tarea</th><th>Estado</th></tr>
                </thead>
                <tbody>
                    {% for item in historial[::-1][:5] %}
                    <tr>
                        <td>{{ item.tarea }}<br><small style="color:#555">{{ item.hora }}</small></td>
                        <td><span class="status-badge {{ 'hecho' if 'HECHO' in item.estado and 'RETRASO' not in item.estado else 'retraso' if 'RETRASO' in item.estado else 'pendiente' }}">
                            {{ item.estado }}
                        </span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # Cuando entres desde el celular, esto es lo que verás
    return render_template_string(HTML_PANEL, historial=db['historial'], rendimiento=db['rendimiento'])

@app.route('/enviar_tarea_web', methods=['POST'])
def enviar_tarea_web():
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
    return '<script>window.location.href="/";</script>'

@app.route('/get_data')
def get_data():
    return jsonify({"tarea": db['tarea_actual'], "tiempo": db['tiempo_actual'], "id": db['id_envio']})

@app.route('/reportar_progreso', methods=['POST'])
def reportar_progreso():
    data = request.json
    id_tarea, estado = data.get('id'), data.get('estado')
    for t in db['historial']:
        if t['id'] == id_tarea:
            t['estado'] = estado
            if "RETRASO" in estado: db['rendimiento']['retrasos'] += 1
            else: db['rendimiento']['exitos'] += 1
            break
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
